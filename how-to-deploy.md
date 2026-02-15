### 1. Initial Setup

- **Push code to GitHub**  
  Push your project code to a GitHub repository.

- **Create a Dockerfile**  
  Write a `Dockerfile` in the root of your project to containerize the app.

- **Create Kubernetes Deployemtn file**  
  Make a file named 'flask-deployment.yaml'

- **Create a VM Instance on Google Cloud**

  - Go to VM Instances and click **"Create Instance"**
  - Name: `flipkart-agent-vm`
  - Machine Type:
    - Series: `E2`
    - Preset: `Standard`
    - Memory: `16 GB RAM`
  - Boot Disk:
    - Change size to `256 GB`
    - Image: Select **Ubuntu 24.04 LTS**
  - Networking:
    - Enable HTTP and HTTPS traffic

- **Create the Instance**

- **Connect to the VM**
  - Use the **SSH** option provided to connect to the VM from the browser.

### 2. Configure VM Instance

- **Clone your GitHub repo**

  ```bash
  git clone https://github.com/your-username/flipkart-shopping-agent.git
  ls
  cd flipkart-shopping-agent
  ls  # You should see the contents of your project
  ```

- **Install Docker**

  - Search: "Install Docker on Ubuntu"
  - Open the first official Docker website (docs.docker.com)
  - Scroll down and copy the **first big command block** and paste into your VM terminal
  - Then copy and paste the **second command block**
  - Then run the **third command** to test Docker:

    ```bash
    docker run hello-world
    ```

- **Run Docker without sudo**

  - On the same page, scroll to: **"Post-installation steps for Linux"**
  - Paste all 4 commands one by one to allow Docker without `sudo`
  - Last command is for testing

- **Enable Docker to start on boot**

  - On the same page, scroll down to: **"Configure Docker to start on boot"**
  - Copy and paste the command block (2 commands):

    ```bash
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    ```

- **Verify Docker Setup**

  ```bash
  systemctl status docker       # You should see "active (running)"
  docker ps                     # No container should be running
  docker ps -a                 # Should show "hello-world" exited container
  ```

### 3. Configure Minikube inside VM

- **Install Minikube**

  - Open browser and search: `Install Minikube`
  - Open the first official site (minikube.sigs.k8s.io) with `minikube start` on it
  - Choose:
    - **OS:** Linux
    - **Architecture:** *x86*
    - Select **Binary download**
  - Reminder: You have already done this on Windows, so you're familiar with how Minikube works

- **Install Minikube Binary on VM**

  - Copy and paste the installation commands from the website into your VM terminal

- **Start Minikube Cluster**

  ```bash
  minikube start
  ```

  - This uses Docker internally, which is why Docker was installed first

- **Install kubectl**

  - Search: `Install kubectl`
  - Run the first command with `curl` from the official Kubernetes docs
  - Run the second command to validate the download
  - Instead of installing manually, go to the **Snap section** (below on the same page)

  ```bash
  sudo snap install kubectl --classic
  ```

  - Verify installation:

    ```bash
    kubectl version --client
    ```

- **Check Minikube Status**

  ```bash
  minikube status         # Should show all components running
  kubectl get nodes       # Should show minikube node
  kubectl cluster-info    # Cluster info
  docker ps               # Minikube container should be running
  ```

### 4. Interlink your Github on VSCode and on VM

```bash
git config --global user.email "your-email@gmail.com"
git config --global user.name "your-username"

git add .
git commit -m "commit"
git push origin main
```

- When prompted:
  - **Username**: `your-github-username`
  - **Password**: GitHub token (paste, it's invisible)

---

### 5. Build and Deploy Your APP on VM (Complete Guide)

**STEP 1: Point Docker to Minikube**
```bash
eval $(minikube docker-env)
```
This tells Docker to use Minikube's internal Docker daemon (important!)

**STEP 2: Build the Docker Image**
```bash
docker build -t flask-app:latest .
```

**STEP 3: Create Kubernetes Secrets**
Replace `"..."` with your actual credentials from AstraDB, Groq, and HuggingFace:
```bash
kubectl create secret generic flipkart-secrets \
  --from-literal=ASTRA_DB_API_ENDPOINT="https://your-astradb-endpoint..." \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="your-token-here..." \
  --from-literal=ASTRA_DB_KEYSPACE="flipkart" \
  --from-literal=GROQ_API_KEY="your-groq-key..." \
  --from-literal=HUGGINGFACEHUB_API_TOKEN="your-huggingface-token..."
```

**STEP 4: Create Monitoring Namespace**
```bash
kubectl create namespace monitoring
kubectl get ns  # Verify it was created
```

**STEP 5: Deploy All Services (Order Matters!)**
```bash
# 1. Deploy Flask App
kubectl apply -f flask-deployment.yaml

# 2. Deploy Prometheus Config
kubectl apply -f prometheus/prometheus-configmap.yaml

# 3. Deploy Prometheus 
kubectl apply -f prometheus/prometheus-deployment.yaml

# 4. Deploy Grafana
kubectl apply -f grafana/grafana-deployment.yaml
```

**STEP 6: Verify All Pods are Running**
```bash
# Check default namespace (Flask app)
kubectl get pods

# Check monitoring namespace (Prometheus & Grafana)
kubectl get pods -n monitoring

# Both should show STATUS: Running
```

### 6. Access Your Application & Monitoring

**Open 3 separate terminal windows on the VM and run these port-forward commands:**

**Terminal 1: Flask App (Port 5000)**
```bash
kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
```
- Access app: `http://<VM-External-IP>:5000`

**Terminal 2: Prometheus Metrics (Port 9090)**
```bash
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090 --address 0.0.0.0
```
- Access: `http://<VM-External-IP>:9090`
- View targets: `http://<VM-External-IP>:9090/targets`
- View metrics: `http://<VM-External-IP>:9090/graph`

**Terminal 3: Grafana Dashboard (Port 3000)**
```bash
kubectl port-forward -n monitoring svc/grafana-service 3000:3000 --address 0.0.0.0
```
- Access: `http://<VM-External-IP>:3000`
- Default login: **admin / admin123**

### 7. Configure Grafana to Show Metrics

1. **Login to Grafana** (http://<VM-External-IP>:3000)
   - Username: `admin`
   - Password: `admin123`

2. **Add Prometheus Data Source:**
   - Go to: Settings (gear icon) → Data Sources
   - Click: "Add data source"
   - Choose: **Prometheus**
   - URL: `http://prometheus-service.monitoring.svc.cluster.local:9090`
   - Click: "Save & Test"
   - You should see: ✓ "Datasource is working"

3. **Create Dashboards:**
   - Go to: Dashboards → New Dashboard
   - Add panels to visualize:
     - `flask_request_total` : Total API requests
     - `flask_request_latency_seconds` : Response times
     - `chat_response_latency_seconds` : RAG agent response time
     - `active_sessions` : Active chat sessions
   - Save your dashboard

### 8. Troubleshooting Deployment

**If pods are stuck in "Pending":**
```bash
kubectl describe pod <pod-name>
kubectl describe pod -n monitoring <pod-name>
```

**If cannot connect to services:**
```bash
# Check service endpoints
kubectl get svc
kubectl get svc -n monitoring

# Check pod logs
kubectl logs <pod-name>
kubectl logs -n monitoring <pod-name>
```

**To restart deployment:**
```bash
kubectl rollout restart deployment/flask-app
kubectl rollout restart deployment/prometheus -n monitoring
kubectl rollout restart deployment/grafana -n monitoring
```

**To delete everything and start over:**
```bash
kubectl delete -f flask-deployment.yaml
kubectl delete -f prometheus/
kubectl delete -f grafana/
kubectl delete namespace monitoring
```

### 9. PROJECT STRUCTURE REFERENCE

```
flipkart-shopping-agent/
├── flask-deployment.yaml     # App Deployment
├── Dockerfile                # Docker Build
├── app.py                    # Backend
├── prometheus/               # Monitoring
│   ├── prometheus-configmap.yaml
│   └── prometheus-deployment.yaml
├── grafana/                  # Visualization
│   └── grafana-deployment.yaml
└── ...
```
