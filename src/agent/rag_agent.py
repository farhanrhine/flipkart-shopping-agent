"""
RAG Agent using LangChain 2026 create_agent API
Uses LangGraph-based agent with tools for retrieval
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from src.config.settings import Config


class RAGAgent:
    """
    RAG Agent using LangChain 2026's create_agent API.
    Uses tools for retrieval instead of chains.
    """
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        self.history_store = {}
        
        # Initialize the model with Groq
        self.model = ChatGroq(
            model=Config.RAG_MODEL,
            temperature=0.5,
            max_tokens=1024,
            timeout=30
        )
        
        # Build the agent
        self.agent = self._build_agent()
    
    def _get_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for a session."""
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]
    
    def _create_retrieval_tool(self):
        """Create a tool for retrieving product information from the vector store."""
        retriever = self.retriever
        
        @tool
        def search_products(query: str) -> str:
            """
            Search for product reviews and information based on the user's query.
            Use this tool to find relevant product information, reviews, and recommendations.
            
            Args:
                query: The search query about products or reviews
                
            Returns:
                Relevant product reviews and information
            """
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant products found for this query."
            
            results = []
            for i, doc in enumerate(docs, 1):
                product_name = doc.metadata.get("product_name", "Unknown Product")
                review = doc.page_content
                results.append(f"**Product {i}: {product_name}**\nReview: {review}\n")
            
            return "\n".join(results)
        
        return search_products
    
    def _build_agent(self):
        """Build the agent with tools and system prompt."""
        
        # Create tools
        tools = [self._create_retrieval_tool()]
        
        # Define system prompt
        system_prompt = SystemMessage(content="""You are a helpful Flipkart shopping assistant powered by AI.

Your role is to help customers with:
- Finding products based on their needs
- Providing product recommendations based on reviews
- Answering questions about product quality, features, and user experiences
- Comparing products when asked

Guidelines:
1. ALWAYS use the search_products tool to find relevant information before answering
2. Base your answers on actual product reviews and information
3. Be concise, helpful, and honest
4. If you don't find relevant information, say so politely
5. When recommending products, explain why based on reviews
6. Highlight both positive and negative aspects mentioned in reviews

Remember: You are an e-commerce assistant helping customers make informed decisions.""")
        
        # Create the agent using LangChain 2026 API
        agent = create_agent(
            self.model,
            tools=tools,
            system_prompt=system_prompt
        )
        
        return agent
    
    def invoke(self, query: str, session_id: str = "default") -> str:
        """
        Invoke the agent with a user query.
        
        Args:
            query: The user's question or request
            session_id: Session ID for conversation history
            
        Returns:
            The agent's response
        """
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Get chat history
        history = self._get_history(session_id)
        
        # Prepare input with history - convert to proper message objects
        messages = list(history.messages) + [HumanMessage(content=query)]
        
        # Invoke the agent
        response = self.agent.invoke({
            "messages": messages
        })
        
        # Extract the answer from response
        answer = ""
        if isinstance(response, dict) and "messages" in response:
            last_message = response["messages"][-1]
            if hasattr(last_message, "content"):
                answer = last_message.content
            elif isinstance(last_message, dict):
                answer = last_message.get("content", "")
        elif hasattr(response, "content"):
            answer = response.content
        else:
            answer = str(response)
        
        # Update history
        history.add_user_message(query)
        history.add_ai_message(answer)
        
        return answer
    
    def stream(self, query: str, session_id: str = "default"):
        """
        Stream the agent's response for real-time output.
        
        Args:
            query: The user's question or request
            session_id: Session ID for conversation history
            
        Yields:
            Chunks of the agent's response
        """
        history = self._get_history(session_id)
        messages = list(history.messages) + [{"role": "user", "content": query}]
        
        full_response = ""
        for chunk in self.agent.stream({"messages": messages}):
            if isinstance(chunk, dict) and "messages" in chunk:
                content = chunk["messages"][-1].get("content", "")
                if content:
                    full_response += content
                    yield content
        
        # Update history after streaming completes
        history.add_user_message(query)
        history.add_ai_message(full_response)

# ==============================================================================
# DEVELOPMENT/TESTING BLOCK - NOT FOR PRODUCTION
# ==============================================================================
# USE THIS WHEN:
#   - Testing the RAG agent standalone: python src/agent/rag_agent.py
#   - Debugging agent responses quickly
#   - Verifying agent works after code changes
#
# DON'T USE THIS WHEN:
#   - Running with Flask/FastAPI (import RAGAgent class instead)
#   - In production deployment
#   - When using as a module in other scripts
#
# To enable: Uncomment the block below
# To disable: Keep commented (default for production)
# ==============================================================================

# if __name__ == "__main__":
#     from src.pipeline.data_ingestion import DataIngestor
#     
#     # Get the vector store
#     ingestor = DataIngestor()
#     vstore = ingestor.ingest(load_existing=True)
#     
#     # Create the agent
#     agent = RAGAgent(vstore)
#     
#     # Test query
#     print("Testing RAG Agent...")
#     response = agent.invoke("What are the best headphones according to reviews?")
#     print(f"\nResponse: {response}")
