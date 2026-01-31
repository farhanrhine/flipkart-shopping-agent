# Step 1: Data Setup

Create `data/` folder and place `flipkart_product_review.csv` file in it.

# Step 2: Utilities

Create `src/utils/` folder:

- `logger.py`: For logging events
- `custom_exception.py`: For handling errors

# Step 3: Configuration

Create `src/config/` folder:

- `settings.py`: To load environment variables (.env)

# Step 4: Pipeline & Data Ingestion

Create `src/pipeline/` folder:

- `data_converter.py`: Converts CSV rows into LangChain Documents
- `data_ingestion.py`: Connects to AstraDB and stores vector embeddings

# Step 5: RAG Agent

Create `src/agent/` folder:

- `rag_agent.py`: Uses LangChain's `create_agent` to build the chatbot
- Uses **Groq (LLM)** + **AstraDB (Vector Store)**
- Implements tools for retrieval and history management

# Step 6: Environment Setup

Create `.env` file with API keys:

- `ASTRA_DB_API_ENDPOINT`
- `ASTRA_DB_APPLICATION_TOKEN`
- `GROQ_API_KEY`

# Step 7: Data Ingestion

Run the ingestion script to populate AstraDB:

```bash
uv run python src/pipeline/data_ingestion.py
```

# Step 8: Flask Application (Backend)

Create `app.py`:

- Initialize RAG Agent
- API Routes: `/chat` (POST), `/clear` (POST), `/metrics` (PROMETHEUS)
- Session management for chat history

# Step 9: Frontend

- `templates/index.html`: Chat interface with Send/Clear buttons
- `static/style.css`: Flipkart-themed styling (Blue #2874f0)

# Step 10: Dockerization

Create `Dockerfile`:

- Base image: `python:3.12-slim`
- Installs `uv` for dependencies
- Exposes port 5000

Build & Run Locally:

```bash
docker build -t flask-app .
docker run -p 5000:5000 --env-file .env flask-app
```

# Step 11: Kubernetes & Monitoring Setup

Organize deployment files:

- `flask-deployment.yaml`: Deployment + Service for Flask App
- `prometheus/`: Monitoring configuration
- `grafana/`: Visualization dashboards

structure:

```
├── flask-deployment.yaml
├── prometheus/
│   ├── prometheus-configmap.yaml
│   └── prometheus-deployment.yaml
├── grafana/
│   └── grafana-deployment.yaml
```

# Step 12: Deployment on GCP (Minikube)

1. Start Minikube
2. Create Secrets for API keys
3. Apply configurations:

   ```bash
   kubectl apply -f flask-deployment.yaml
   kubectl apply -f prometheus/
   kubectl apply -f grafana/
   ```

# Summary of Features

- **Backend**: Flask + LangChain + Groq + AstraDB
- **Frontend**: HTML/CSS Chat Interface
- **Monitoring**: Prometheus (Metrics) + Grafana (Visuals)
- **Deployment**: Dockerized & Kubernetes Ready
