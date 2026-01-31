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

    def ingest(self,load_existing=True):
        if load_existing==True:
            return self.vstore
        
        csv_path = str(PROJECT_ROOT / "data" / "flipkart_product_review.csv")
        docs = DataConverter(csv_path).convert()

        self.vstore.add_documents(docs)

        return self.vstore

if __name__=="__main__":
    ingestor = DataIngestor()
    ingestor.ingest(load_existing=False)