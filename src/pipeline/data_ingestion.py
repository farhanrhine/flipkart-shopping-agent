import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from src.pipeline.data_converter import DataConverter
from src.config.settings import Config


class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEndpointEmbeddings(model=Config.EMBEDDING_MODEL)

        print(f"Connecting to AstraDB...")
        print(f"Endpoint: {Config.ASTRA_DB_API_ENDPOINT}")
        print(f"Keyspace: {Config.ASTRA_DB_KEYSPACE}")
        
        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="flipkart_database",
            api_endpoint=Config.ASTRA_DB_API_ENDPOINT,
            token=Config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=Config.ASTRA_DB_KEYSPACE
        )

    def ingest(self, load_existing=True):
        """
        Ingest documents into the vector store.
        
        Args:
            load_existing: If True, just return existing vstore without adding docs.
                          If False, add documents only if collection is empty.
        """
        if load_existing:
            print("Using existing vector store connection.")
            return self.vstore
        
        # Check if collection already has data
        try:
            # Try to get a sample document to check if data exists
            results = self.vstore.similarity_search("test", k=1)
            if results:
                print(f"Collection already has data ({len(results)}+ documents). Skipping ingestion.")
                print("To re-ingest, delete the collection in AstraDB first.")
                return self.vstore
        except Exception:
            pass  # Collection might be empty, proceed with ingestion
        
        print("Ingesting documents...")
        csv_path = str(PROJECT_ROOT / "data" / "flipkart_product_review.csv")
        docs = DataConverter(csv_path).convert()
        print(f"Found {len(docs)} documents to ingest.")

        self.vstore.add_documents(docs)
        print("Ingestion complete!")

        return self.vstore

# ==============================================================================
# DEVELOPMENT/TESTING BLOCK - NOT FOR PRODUCTION
# ==============================================================================
# USE THIS WHEN:
#   - First time data ingestion: python src/pipeline/data_ingestion.py
#   - Re-ingesting data after CSV changes
#   - Testing database connection
#
# DON'T USE THIS WHEN:
#   - Running with Flask/FastAPI (import DataIngestor class instead)
#   - Data already ingested in AstraDB
#   - In production deployment
#
# WARNING: Running with load_existing=False will add duplicate data!
#          Delete collection in AstraDB first if re-ingesting.
#
# To enable: Uncomment the block below
# To disable: Keep commented (default for production)
# ==============================================================================

# if __name__ == "__main__":
#     ingestor = DataIngestor()
#     ingestor.ingest(load_existing=False)
