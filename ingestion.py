import uuid
from typing import List, Dict, Any
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding
from config import settings

class DocumentIngestor:
    def __init__(self):
        # 1. Setup Parsers and Chunkers
        self.converter = DocumentConverter()
        self.chunker = HybridChunker() # Retains hierarchy and bounding boxes
        
        # 2. Setup Embedding Models (Dense + Sparse)
        self.dense_model = TextEmbedding(model_name=settings.DENSE_MODEL_NAME)
        self.sparse_model = SparseTextEmbedding(model_name=settings.SPARSE_MODEL_NAME)
        
        # 3. Setup Qdrant Client
        self.qdrant = QdrantClient(url=settings.QDRANT_URL)
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Creates a Qdrant collection configured for hybrid search if it doesn't exist."""
        if not self.qdrant.collection_exists(settings.QDRANT_COLLECTION):
            # Dense vectors represent semantic meaning (dimensions depend on model, MiniLM is 384)
            # Sparse vectors represent exact keyword tokens (BM25/SPLADE)
            self.qdrant.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config={
                    "dense": models.VectorParams(size=384, distance=models.Distance.COSINE)
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
                }
            )

    def process_and_index(self, file_path: str) -> str:
        """Parses a PDF, chunks it spatially, and indexes it into Qdrant."""
        doc_id = str(uuid.uuid4())
        
        # 1. Parse Layout and Text
        docling_doc = self.converter.convert(file_path).document
        
        # 2. Chunk with Layout Preservation
        chunks = self.chunker.chunk(docling_doc)
        
        points = []
        for i, chunk in enumerate(chunks):
            text_content = chunk.text
            
            # Extract Bounding Box and Page metadata if available
            bbox_data = None
            page_no = None
            if chunk.meta and chunk.meta.prov:
                prov = chunk.meta.prov[0] # Take primary provenance block
                page_no = prov.page_no
                bbox_data = {
                    "x0": prov.bbox.l, "y0": prov.bbox.t, 
                    "x1": prov.bbox.r, "y1": prov.bbox.b
                }

            # 3. Generate Embeddings
            dense_vec = list(self.dense_model.embed([text_content]))[0].tolist()
            sparse_vec = list(self.sparse_model.embed([text_content]))[0]
            
            # Format sparse vector for Qdrant
            qdrant_sparse = models.SparseVector(
                indices=sparse_vec.indices.tolist(),
                values=sparse_vec.values.tolist()
            )

            # 4. Construct Payload
            payload = {
                "doc_id": doc_id,
                "chunk_index": i,
                "text": text_content,
                "page": page_no,
                "bbox": bbox_data
            }

            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector={"dense": dense_vec, "sparse": qdrant_sparse},
                    payload=payload
                )
            )

        # 5. Upsert to Vector Database
        self.qdrant.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points,
            wait=True
        )
        
        return doc_id

    def hybrid_search(self, query: str, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Performs a hybrid search (Dense + Sparse) filtered by document ID."""
        dense_vec = list(self.dense_model.embed([query]))[0].tolist()
        sparse_vec = list(self.sparse_model.embed([query]))[0]
        
        qdrant_sparse = models.SparseVector(
            indices=sparse_vec.indices.tolist(),
            values=sparse_vec.values.tolist()
        )

        # Use Qdrant's Prefetch with Reciprocal Rank Fusion (RRF)
        prefetch = [
            models.Prefetch(query=dense_vec, using="dense", limit=limit),
            models.Prefetch(query=qdrant_sparse, using="sparse", limit=limit),
        ]

        results = self.qdrant.search(
            collection_name=settings.QDRANT_COLLECTION,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            query_filter=models.Filter(
                must=[models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))]
            ),
            limit=limit
        )

        return [res.payload for res in results]