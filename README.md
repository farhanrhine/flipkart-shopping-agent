# Flipkart Shopping Agent

A powerful RAG-based (Retrieval-Augmented Generation) recommender system designed to provide intelligent product recommendations from the Flipkart dataset.

## 🚀 Tech Stack

- **Backend Framework:** [Flask](https://flask.palletsprojects.com/)
- **AI Orchestration:** [LangChain](https://www.langchain.com/)
- **LLM & Embeddings:** [Groq](https://groq.com/) / [HuggingFace](https://huggingface.co/)
- **Vector Database:** [AstraDB](https://www.datastax.com/products/astra) (DataStax)
- **Data Analysis:** [Pandas](https://pandas.pydata.org/) & [Datasets](https://huggingface.co/docs/datasets/)
- **Monitoring & Metrics:** [Prometheus](https://prometheus.io/) & [Grafana](https://grafana.com/)
- **Package Management:** [UV](https://github.com/astral-sh/uv)
- **Containerization:** [Docker](https://www.docker.com/) & [Kubernetes](https://kubernetes.io/)

## 🏗️ Architecture

![Architecture](architecture.png)

## 📂 Project Structure

```text
flipkart-shopping-agent/
├── data/                    # Raw and processed data storage
├── src/                     # Core application logic
│   ├── agent/               # RAG agent implementation
│   │   └── rag_agent.py     # RAG pipeline and LangChain logic
│   ├── config/              # Configuration management
│   │   └── settings.py      # Configuration and environment settings
│   ├── pipeline/            # Data processing pipeline
│   │   ├── data_converter.py    # Scripts for data format conversions
│   │   └── data_ingestion.py    # Logic for loading data into AstraDB
│   └── utils/               # Helper utilities
│       ├── custom_exception.py  # Standardized error handling
│       └── logger.py            # Application logging configuration
├── grafana/                 # Grafana monitoring dashboards
├── prometheus/              # Prometheus metrics configuration
├── static/                  # Static assets for the web interface
├── templates/               # HTML templates for Flask
├── app.py                   # Flask web server entry point
├── main.py                  # Main execution script
├── Dockerfile               # Docker image configuration
├── pyproject.toml           # Project metadata and dependencies
└── flask-deployment.yaml    # Kubernetes deployment manifest
```

## 🛠️ Getting Started

1. **Clone the repository**
2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file with your credentials (AstraDB, Groq, etc.)
4. **Run the application:**

   ```bash
   python app.py
   ```
