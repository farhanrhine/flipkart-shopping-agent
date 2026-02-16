---

## Technology Stack for This Deployment

This guide deploys your **Flipkart Shopping Agent** using modern DevOps and containerization technologies:

| Technology | Purpose | Why? |
|-----------|---------|------|
| **Google Cloud Platform (GCP)** | Cloud hosting | Scalable, reliable cloud infrastructure (~$0.15/hour) |
| **Ubuntu 24.04 LTS** | Operating System | Server OS with security updates & stability |
| **Docker** | Containerization | Package app with all dependencies, run anywhere |
| **Kubernetes (Minikube)** | Container Orchestration | Manage, scale, and monitor containers automatically |
| **Flask** | Web Framework | Lightweight Python backend for your AI agent |
| **Prometheus** | Metrics Collection | Monitors app performance, resource usage in real-time |
| **Grafana** | Data Visualization | Beautiful dashboards showing Prometheus metrics |
| **Git & GitHub** | Version Control | Track code changes, deploy from repository |

**You'll also use:**
- **Kubernetes Secrets** - Securely store API keys (AstraDB, Groq, HuggingFace tokens)
- **kubectl** - Command-line tool to manage Kubernetes
- **Port Forwarding** - Access services running inside Kubernetes from outside VM

**Why this stack?**
- **Docker** = Consistent deployment (works on any machine)
- **Kubernetes** = Professional-grade container management (used by Netflix, Google, Amazon)
- **Prometheus + Grafana** = Monitor app health and performance like major companies do
- **Self-hosted** = You own your infrastructure, no vendor lock-in

---

### 1. Initial Setup

**Prerequisites:**
- Push code to GitHub
- Create a `Dockerfile` in project root
- Create `flask-deployment.yaml` file

**Create VM Instance on Google Cloud:**

1. Go to VM Instances and click **"Create Instance"**
2. Configure instance:
   - **Name:** `flipkart-agent-vm`
   - **Machine Type:**
     - Series: `E2`
     - Preset: `Standard`
     - Memory: `16 GB RAM`
   - **Boot Disk:**
     - Size: `256 or 150 GB`
     - Image: **Ubuntu 24.04 LTS x86_64 amd64 noble build in 2025-06-06**
     - Cost: ~$0.15/hour = ~$112.84/month (AWS charges 2-3x more for similar specs)
   - **Networking & Firewall:**
     - Enable HTTP and HTTPS traffic and load balancing (opens ports 80, 443)
     - **Enable IP forwarding** (important for Kubernetes inside VM)
     - Rest left as default
3. Click **Create** to launch (takes 1-2 minutes)

**Connect to the VM:**

- Click **SSH** button next to your VM in Google Cloud Console
- Browser opens with terminal connected to your VM
- Click **Allow** when asked to authorize
- Type `clear` to clean the terminal



### 2. Install Docker on VM

**Install Docker:**

1. Search: "Install Docker on Ubuntu"
2. Go to official Docker website (docs.docker.com)
3. Find **Install using the apt repository** section: https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
4. Paste commands into your VM terminal
5. If asked Yes/No, type `Y` and press Enter
6. Test Docker:

   ```bash
   sudo docker run hello-world
   ```
   You should see "Hello from Docker!" confirming successful installation.

**Run Docker without `sudo`:**

Go to: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user

Paste all commands one by one to allow Docker without `sudo`

**Enable Docker to Start on Boot:**

Go to: https://docs.docker.com/engine/install/linux-postinstall/#configure-docker-to-start-on-boot-with-systemd

Paste the commands:

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

This automatically starts Docker service when VM boots.

**Verify Docker Setup:**

```bash
docker --version              # Should show Docker version
systemctl status docker       # Should see "active (running)"
docker ps                     # No container should be running
docker ps -a                  # Should show "hello-world" exited container
```

### 3. Install and Configure Minikube & kubectl

Minikube is a dependency of Docker - we need Docker first, then Minikube. Minikube will use the Docker engine inside the VM to create and manage the Kubernetes cluster.

**Install Minikube:**

Go to: https://minikube.sigs.k8s.io/docs/start/

Select:
- **OS:** Linux
- **Architecture:** x86
- **Release:** Stable
- **Driver:** Binary download

Copy and paste the 2 installation commands:

```bash
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

**Start Minikube Cluster:**

```bash
minikube start
```

This creates your Kubernetes cluster running inside the VM using Docker. This may take a few minutes. You should see output indicating Minikube is setting up the cluster.

**Install kubectl (Kubernetes CLI):**

Go to: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-other-package-management

Install using Snap (easiest for Ubuntu since snap is pre-installed):

```bash
sudo snap install kubectl --classic
```

The `--classic` flag allows kubectl to access system resources it needs on your VM.

Verify installation:

```bash
kubectl version --client
```

**Check Minikube Status:**

```bash
minikube status         # Should show all components running
kubectl get nodes       # Should show minikube node
kubectl cluster-info    # Shows cluster information
docker ps               # Minikube container should be running
```

  
> ⚠️ **IMPORTANT BEFORE DEPLOYING:**
>
> Update the `prometheus-configmap.yaml` file's `scrape_configs` section. Replace `<VM-External-IP>` with your actual external IP address:
>
> ```yaml
> scrape_configs:
>   - job_name: 'prometheus'
>     static_configs:
>       - targets: ['localhost:9090']
>   
>   - job_name: 'flask-app'
>     metrics_path: /metrics
>     static_configs:
>       - targets: ['<VM-External-IP>:5000']  # e.g., ['34.42.228.136:5000']
> ```
>
> **Why this is needed:** Prometheus has two scrape targets:
> - **Target 1** (`localhost:9090`): Prometheus monitors itself
> - **Target 2** (`<VM-External-IP>:5000`): Prometheus monitors your Flask app
>
> Without this configuration, Prometheus won't connect to your Flask app. This ensures your application's performance metrics are properly collected for Grafana visualization.



---

### 4. Clone Repository & Configure Git

You need to connect 3 environments: local VSCode → GitHub → GCP VM. This allows you to push changes from local to GitHub, then pull them on the VM for deployment.

**Clone your GitHub repository:**

```bash
git clone https://github.com/farhanrhine/flipkart-shopping-agent.git
cd flipkart-shopping-agent
ls  # Verify you see all project files
```

**Configure Git on VM:**

```bash
git config --global user.email "your-email@example.com"    # Your email
git config --global user.name "your-github-username"        # Your GitHub username
```

**Using GitHub Personal Access Token (Required):**

GitHub no longer allows password authentication for Git operations. You must use a Personal Access Token instead.

**How to get GitHub token:**

1. Go to GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token**
3. Configure:
   - **Name:** `VM Deployment Token`
   - **Expiration:** `No expiration`
   - **Scopes:** Check:
     - `repo` (for repository access)
     - `workflow` (for GitHub Actions)
     - `admin-org` (for organization management)
     - `admin:repo_hook` (for webhooks)
     - `admin:org_hook` (for organization webhooks)
4. Click **Generate token**
5. **Copy the token** (you won't see it again!)

**Version Control Workflow:**

1. Make changes locally in VSCode
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
3. When prompted:
   - **Username:** Your GitHub username
   - **Password:** Paste your Personal Access Token (invisible when pasting)
4. Pull latest changes on VM before deploying:
   ```bash
   git pull origin main
   ```

This is called version control - it's essential for managing code changes across different environments and ensuring you can easily update and maintain your application as you develop it.

---

### 5. Configure GCP Firewall Rules

By default, only ports 80 (HTTP) and 443 (HTTPS) are open. We need to allow custom ports for:
- **5000** - Flask app
- **9090** - Prometheus metrics  
- **3000** - Grafana dashboard

**Create Firewall Rule:**

1. Go to Google Cloud Console → **Compute Engine → VPC networks → Firewall rules**
2. Click **"Create Firewall Rule"**
3. Configure:
   - **Name:** `allow-flask-prometheus-grafana` (or any descriptive name)
   - **Network:** Select the default network (or the one your VM is in)
   - **Direction of traffic:** Ingress
   - **Action on match:** Allow
   - **Targets:** All instances in the network (or specify your VM instance)
   - **Source filter:** IPv4 ranges
   - **Source IP ranges:** `0.0.0.0/0` (allows traffic from any IP address)
   - **Protocols and ports:**
     - Select "Allow all" OR specify:
       - Protocol: TCP, Port: **5000** (Flask app)
       - Protocol: TCP, Port: **9090** (Prometheus)
       - Protocol: TCP, Port: **3000** (Grafana)
4. Click **"Create"** to save the firewall rule




### 6. Build and Deploy Your Application on VM

**Step 1: Navigate to your project folder**

In the SSH browser terminal:

```bash
clear                          # Clear the terminal
cd flipkart-shopping-agent     # Go inside the project folder
ls                             # Verify all project files
```

**Step 2: Point Docker to Minikube**

```bash
eval $(minikube docker-env)
```

This tells Docker to use Minikube's internal Docker daemon. Images built here are immediately available in the cluster without needing to push to an external registry. (This may take a moment to execute.)

**Step 3: Build the Docker Image**

```bash
docker build -t flask-app:latest .
```

**Important:** This image name matches the `flask-deployment.yaml` file. If you change it, update the deployment file too.

Verify the image was built:

```bash
docker images
```

You should see `flask-app` or `flask-app:latest` in the list.

**Step 4: Create Kubernetes Secrets**

This must be done in your project directory (`flipkart-shopping-agent`) since we need the credentials from the `.env` file in the project root.

Replace the placeholders with your actual credentials from AstraDB, Groq, and HuggingFace:

```bash
kubectl create secret generic flipkart-secrets \
  --from-literal=ASTRA_DB_API_ENDPOINT="https://your-astradb-endpoint..." \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="your-token-here..." \
  --from-literal=ASTRA_DB_KEYSPACE="flipkart" \
  --from-literal=GROQ_API_KEY="your-groq-key..." \
  --from-literal=HUGGINGFACEHUB_API_TOKEN="your-huggingface-token..."
```

This securely stores all your sensitive credentials in Kubernetes secrets. Your Flask app can access them without hardcoding them in code or configuration files. This is a best practice for managing sensitive information.

Expected message: `secret/flipkart-secrets created` - means the secrets were successfully created!

**Step 5: Deploy Flask App**

In your project directory:

```bash
kubectl apply -f flask-deployment.yaml
```

Expected message: `deployment.apps/flask-app created`

Verify Flask app is running:

```bash
kubectl get pods
```

You should see a pod with name "flask-app" and status "Running". If not running, check logs:

```bash
kubectl logs <flask-app-pod-name>
```

**Step 6: Create Monitoring Namespace**

Check existing namespaces:

```bash
kubectl get ns
```

Create a namespace for monitoring components:

```bash
kubectl create namespace monitoring
```

**Why "monitoring"?** The Prometheus and Grafana deployment files have namespace set to monitoring. It needs to match exactly.

Verify namespace creation:

```bash
kubectl get ns
```

You should see "monitoring" listed.

**Step 7: Deploy Monitoring Stack (Order Matters!)**

⚠️ **Important:** Deploy Prometheus FIRST because Grafana needs to connect to Prometheus as a data source. If Prometheus isn't deployed and running, Grafana won't be able to connect to it.

Deploy in this order:

```bash
# 1. Deploy Prometheus Configuration
kubectl apply -f prometheus/prometheus-configmap.yaml
# Expected: "configmap/prometheus-config created"

# 2. Deploy Prometheus Server
kubectl apply -f prometheus/prometheus-deployment.yaml
# Expected: "deployment.apps/prometheus created"

# 3. Deploy Grafana for Visualization
kubectl apply -f grafana/grafana-deployment.yaml
# Expected: "deployment.apps/grafana created"
```

**Step 8: Verify All Pods are Running**

```bash
# Check default namespace (Flask app)
kubectl get pods

# Check monitoring namespace (Prometheus & Grafana)
kubectl get pods -n monitoring
```

Both should show STATUS: **Running**

If status shows `ContainerCreating`, wait a moment and check again.

If status shows `Error` or `CrashLoopBackOff`, check pod logs:

```bash
kubectl logs -n monitoring <pod-name>
```

---

### 7. Access Your Application via Port Forwarding

Your application is running inside the Kubernetes cluster (which runs inside the VM). To access it externally, we use port forwarding.

> ⚠️ **Checkpoint:** Flask app deployed successfully! Now set up port forwarding to access it externally.

**Important:** Open 3 separate SSH terminal windows on the VM for port forwarding.

**Terminal 1: Flask App (Port 5000)**

```bash
kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
```

Expected message: `Forwarding from 0.0.0.0:5000 -> 80`

Access your app: `http://<VM-External-IP>:5000`

**Note:** The `flask-service` name matches your `flask-deployment.yaml` file. If you change it in the deployment file, update it here too.

The `--address 0.0.0.0` flag allows connections from any IP address. Without it, port forwarding only accepts localhost connections.

If you get an error:
- Check firewall rules allow port 5000
- Check pod status: `kubectl get pods`
- Check pod logs: `kubectl logs <flask-app-pod-name>`

**Terminal 2: Prometheus Metrics (Port 9090)**

```bash
kubectl port-forward svc/prometheus-service 9090:9090 -n monitoring --address 0.0.0.0
```

Expected message: `Forwarding from 0.0.0.0:9090 -> 9090`

Access Prometheus: `http://<VM-External-IP>:9090`

Check if Prometheus is scraping metrics correctly:

```
http://<VM-External-IP>:9090/targets
```

You should see 2 targets:
- **prometheus** → UP (localhost:9090) - Prometheus monitoring itself
- **flask-app** → UP (<VM-External-IP>:5000) - Prometheus monitoring your Flask app

If both show UP (green), metrics collection is working!

View metrics graph: `http://<VM-External-IP>:9090/graph`

**Terminal 3: Grafana Dashboard (Port 3000)**

```bash
kubectl port-forward svc/grafana-service 3000:3000 -n monitoring --address 0.0.0.0
```

Expected message: `Forwarding from 0.0.0.0:3000 -> 3000`

Access Grafana: `http://<VM-External-IP>:3000`

Default login credentials:
- **Username:** `admin`
- **Password:** `admin123` (set in `grafana-deployment.yaml`)

The port number is important - all services use the same external IP, but different ports tell which service you're accessing.

**Find Your VM's External IP:**

Go to Google Cloud Console → **Compute Engine → VM Instances** and look for your instance. Copy the external IP address (example: `34.42.228.136`).


> **now this is how you deploy prometheus and grafana monitoring of your application**

check the namespace for monitoring components

```bash
kubectl get ns
```

By default you'll see:
```
NAME              STATUS   AGE
default           Active   20m
kube-node-lease   Active   20m
kube-public       Active   20m
kube-system       Active   20m
```

The default namespace is where your Flask app runs. The last 3 are Kubernetes system namespaces. We'll create a separate namespace for monitoring to keep things organized.

Create a new namespace for monitoring:

```bash
kubectl create namespace monitoring
```

Verify it was created:

```bash
kubectl get ns
```

You should see "monitoring" in the list.

> ⚠️ **CRITICAL: Deployment Order Matters!**
>
> Deploy **Prometheus FIRST**, then Grafana. If you deploy them in the wrong order:
> - Grafana won't be able to connect to Prometheus as a data source
> - Metrics won't be visualized
> - Deployment will fail
>
> **Also Important:** The directory and file names must match your GitHub repo exactly, otherwise it breaks 💥

```bash
# 1. Deploy Prometheus Config
kubectl apply -f prometheus/prometheus-configmap.yaml # you see msg like "configmap/prometheus-config created" it means the Prometheus configuration is successfully created in Kubernetes and you can proceed to deploy the Prometheus server which will use this configuration to scrape metrics from your Flask app and itself.

# 2. Deploy Prometheus 
kubectl apply -f prometheus/prometheus-deployment.yaml # same here, you should see a message like "deployment.apps/prometheus created" it means the Prometheus deployment is successfully created in Kubernetes and you can proceed to deploy Grafana to visualize the metrics collected by Prometheus.

# 3. Deploy Grafana
kubectl apply -f grafana/grafana-deployment.yaml # you should see a message like "deployment.apps/grafana created" it means the Grafana deployment is successfully created in Kubernetes and you can proceed to verify that all pods (Flask app, Prometheus, Grafana) are running correctly before accessing them.
```



---

### 8. Configure Grafana to Show Metrics

> ℹ️ **About Accounts: Self-Hosted vs Cloud Services**
>
> **When you DON'T need accounts (like this project):**
> - Self-hosted Prometheus & Grafana running on your own VM/Kubernetes
> - You own the infrastructure
> - Use local default credentials (admin/admin123)
> - No external sign-ups needed
>
> **When you DO need accounts:**
> - Using **Grafana Cloud** (managed service by Grafana Labs)
> - Using **Prometheus Cloud** or external monitoring services
> - Using 3rd-party SaaS platforms
> - These require email/password signup
>
> **This project uses self-hosted approach** → no accounts needed, just use default credentials below.

**Login to Grafana:**

- Go to: `http://<VM-External-IP>:3000`
- Username: `admin`
- Password: `admin123` (set in `grafana-deployment.yaml`)

**Add Prometheus as Data Source:**

1. Search bar (top left) → type "Data Sources"
2. Click **"Add data source"**
3. Select **Prometheus**
4. Configure:
   - **Name:** "Prometheus" (or any name you prefer)
   - **URL:** `http://prometheus-service.monitoring.svc.cluster.local:9090`
   
   This is the internal URL for Prometheus within the Kubernetes cluster. It should match the service name and namespace in your `prometheus-deployment.yaml` file.

5. Click **"Save & Test"**
6. You should see: ✓ **"Successfully queried the Prometheus API"** (green) - Grafana is connected!

**Create Dashboards:**

1. Click **Dashboards** (left menu) → **"New Dashboard"**
2. Click **"Add a new panel"**
3. In the **Metrics** dropdown, select metrics to visualize:
   - `flask_request_total` - Total API requests
   - `flask_request_latency_seconds` - Response times
   - `chat_response_latency_seconds` - RAG agent response time
   - `active_sessions` - Active chat sessions
   - Check `app.py` for more available metrics
4. Set label filter as `instance` to see metrics per instance (if you have multiple)
5. Click **"Run queries"** to preview
6. Click **"Save"** and name your dashboard (e.g., "Flask App Metrics")

**View Metrics in Real-Time:**

Chat with your Flask app to generate traffic and watch the metrics update live on your Grafana dashboard!

Create additional panels by clicking "Add another visualization" and selecting different metrics.

### 9. Troubleshooting Deployment

**Problem: Pods Stuck in "Pending" Status**

Get detailed information about the pod:
```bash
kubectl describe pod <pod-name>
kubectl describe pod -n monitoring <pod-name>
```

This shows events and conditions preventing the pod from running (usually resource constraints or image pull issues).

**Problem: Cannot Connect to Services**

Check available services:
```bash
kubectl get svc
kubectl get svc -n monitoring
```

Check pod logs for error messages:
```bash
kubectl logs <pod-name>
kubectl logs -n monitoring <pod-name>
```

**Solution: Restart Deployments**

If a service is not responding, restart it:
```bash
kubectl rollout restart deployment/flask-app
kubectl rollout restart deployment/prometheus -n monitoring
kubectl rollout restart deployment/grafana -n monitoring
```

**Nuclear Option: Delete Everything & Start Fresh**

If you need to completely reset:
```bash
kubectl delete -f flask-deployment.yaml
kubectl delete -f prometheus/
kubectl delete -f grafana/
kubectl delete namespace monitoring
```

Then redeploy from [Step 2: Deploy Prometheus & Grafana](#deploy-prometheus--grafana).

### 10. Project Structure Reference

Here's the directory organization for this deployment:

```
flipkart-shopping-agent/
├── flask-deployment.yaml     # Kubernetes Flask App Deployment
├── Dockerfile                # Docker image build configuration
├── app.py                    # Flask backend server
├── prometheus/               # Prometheus monitoring setup
│   ├── prometheus-configmap.yaml    # Prometheus configuration
│   └── prometheus-deployment.yaml   # Prometheus deployment
├── grafana/                  # Grafana visualization setup
│   └── grafana-deployment.yaml      # Grafana deployment
├── src/                      # Source code (agent, pipeline, config, utils)
└── ...
```

**Key Files:**
- **flask-deployment.yaml** - Defines how Flask app runs in Kubernetes (replicas, ports, environment variables)
- **Dockerfile** - Specifies how to build the Docker image for your Flask app
- **prometheus-configmap.yaml** - Tells Prometheus which services to monitor and how to scrape metrics
- **prometheus-deployment.yaml** - Runs Prometheus in Kubernetes
- **grafana-deployment.yaml** - Runs Grafana for visualization

### 11. Clean Up Resources (Avoid Unnecessary Costs)

After completing development/testing, clean up resources to prevent ongoing charges (~$0.15/hour = $112.84/month).

**Delete the VM Instance:**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Compute Engine** → **VM Instances**
3. Find your VM instance (e.g., `flipkart-agent-vm`)
4. Click **⋮** (three dots) next to the instance → select **Delete**
5. Confirm deletion (takes 3-4 minutes to complete)

Once deleted, charges for this instance stop immediately.

**Optional: Delete Associated Resources**

If created specifically for this project, also delete:

- **Disks** - Any persistent disks not attached to running instances
- **Firewall Rules** - Rules you created for ports 5000, 9090, 3000
  - Go to **VPC Network** → **Firewall Rules**
  - Find and delete rules created for this project
- **VPC Networks** - If you created a custom network specifically for this project

**Cost Savings Tip:**

> ⚠️ **Always clean up resources after use.** Even a "stopped" VM instance can incur storage costs. Always **delete** instead of just stopping if you won't use it again.

Always verify deletion is complete before closing the Cloud Console to ensure you won't be charged for forgotten resources.
