# 🛒 Flipkart Shopping Agent

A powerful **Retrieval-Augmented Generation (RAG)** chatbot designed to help users find products, analyze reviews, and get recommendations based on Flipkart product data. Built with **Flask**, **LangChain**, **Groq**, and **AstraDB**.

**What is this?**
This is an AI-powered shopping assistant that helps users find products on Flipkart. It uses **RAG (Retrieval-Augmented Generation)** to look up real product reviews and specifications to give honest, data-backed recommendations.

---

## 🏗️ Architecture

![Architecture](architecture.png)

This project follows a modern **LLMOps** workflow, integrating data ingestion, vector storage, and an autonomous agent to answer user queries effectively.

---

## ⚡ How It Works (The Flow)

1. **User Asks a Question:** "What are the best headphones under 2000?"
2. **App Receives Request:** `app.py` gets the message at the `/chat` endpoint.
3. **Agent takes over:** The `RAGAgent` (in `src/agent/rag_agent.py`) wakes up.
4. **Information Retrieval:**
    - The agent uses a tool called `search_products`.
    - This tool searches **AstraDB** (a vector database) for products that match "best headphones" and "under 2000".
5. **AI Thinking:**
    - The retrieved product reviews are sent to **Groq** (a really fast AI model provider).
    - The AI reads the reviews and drafts a helpful response.
6. **Response:** The answer is sent back to `app.py` and displayed on your screen.

---

## 🔄 RAG Pipeline & Data Flow

### 1. Data Ingestion Pipeline

The system ingests product reviews from CSV, converts them into vector embeddings, and stores them in AstraDB.

![Pipeline Flow](src/pipeline/flowofpipeline.png)

### 2. Vector Database Structure

We use **AstraDB (Cassandra)** as our vector store to enable semantic search capabilities.

![Vector Data Details](src/pipeline/vector-data-details.png)

---

## 🛠️ Tech Stack

- **LLM**: Groq (Llama3 / Mixtral)
- **Embeddings**: HuggingFace (`BAAI/bge-base-en-v1.5`)
- **Vector DB**: DataStax AstraDB (Cassandra)
- **Framework**: LangChain (Agents & Tools)
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3 (Flipkart Theme)
- **Monitoring**: Prometheus & Grafana
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube / GKE)

---

## 🚀 Quick Start (Local)

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/flipkart-shopping-agent.git
   cd flipkart-shopping-agent
   ```

2. **Install Dependencies**

   ```bash
   pip install uv
   uv pip install -r pyproject.toml
   ```

3. **Set up Environment Variables**
   Create a `.env` file:

   ```env
   ASTRA_DB_API_ENDPOINT=...
   ASTRA_DB_APPLICATION_TOKEN=...
   GROQ_API_KEY=...
   HUGGINGFACEHUB_API_TOKEN=...
   ```

4. **Run Ingestion (First time only)**

   ```bash
   uv run python src/pipeline/data_ingestion.py
   ```

5. **Start Application**

   ```bash
   uv run python app.py
   ```

   Visit `http://localhost:5000` to chat!

---

## 🔍 Key Files Guide

If you want to understand or modify the code, here are the most important files:

- **`app.py`**: The main entry point. Runs the Flask server and handles the `/chat` API.
- **`src/agent/rag_agent.py`**: The AI logic. Where the LangChain agent lives, talks to Groq, and searches the database.
- **`src/pipeline/data_ingestion.py`**: Handles loading your CSV data into AstraDB so the AI can search it.
- **`templates/index.html`**: The frontend chat interface.
- **`src/config/settings.py`**: Where environment variables and configuration settings are loaded.

---

## 📦 Deployment

For full deployment instructions on **Google Cloud Platform (GCP)** using **Minikube** and **Kubernetes**, please refer to:
👉 [**FULL-DOCUMENTATION.md**](FULL-DOCUMENTATION.md)

---

## 📊 Monitoring

The application includes built-in monitoring:

- **Prometheus**: `/metrics` endpoint
- **Grafana**: Visual dashboards for request latency and error rates

---

## 📂 Project Structure

```bash
flipkart-shopping-agent/
├── .github/                   # 🤖 GitHub Actions workflows
├── data/                      
│   └── flipkart_product_review.csv  # 💾 Raw dataset
├── grafana/
│   └── grafana-deployment.yaml      # 📈 Grafana K8s deployment
├── prometheus/
│   ├── prometheus-configmap.yaml    # ⚙️ Monitoring config
│   └── prometheus-deployment.yaml   # 🔍 Prometheus K8s deployment
├── src/
│   ├── agent/
│   │   └── rag_agent.py             # 🧠 Main RAG Logic (LangChain)
│   ├── config/
│   │   └── settings.py              # ⚙️ Environment settings
│   ├── pipeline/
│   │   ├── data_converter.py        # 🔄 CSV to Document converter
│   │   └── data_ingestion.py        # 💉 AstraDB Ingestion script
│   └── utils/
│       ├── custom_exception.py      # ⚠️ Error handling
│       └── logger.py                # 📝 System logging
├── static/
│   └── style.css                    # 🎨 Frontend styling
├── templates/
│   └── index.html                   # 🖥️ Frontend UI
├── app.py                           # 🏁 Flask Application Entry Point
├── Dockerfile                       # 🐳 Docker build instructions
├── flask-deployment.yaml            # ☸️ Main Kubernetes App Deployment
├── pyproject.toml                   # 🐍 Python dependencies
├── FULL-DOCUMENTATION.md            # 📚 Detailed Deployment Guide
├── README.md                        # 📖 Project Overview
└── .gitignore                       # 🙈 Git ignore rules
```
