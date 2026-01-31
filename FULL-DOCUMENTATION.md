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

### 5. Build and Deploy your APP on VM

```bash
## Point Docker to Minikube (Important!)
eval $(minikube docker-env)

## Build the image
docker build -t flask-app:latest .

## Create Secrets (Replace "..." with your actual keys)
kubectl create secret generic flipkart-secrets \
  --from-literal=ASTRA_DB_API_ENDPOINT="..." \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="..." \
  --from-literal=ASTRA_DB_KEYSPACE="flipkart" \
  --from-literal=GROQ_API_KEY="..." \
  --from-literal=HUGGINGFACEHUB_API_TOKEN="..."

## Deploy the app
kubectl apply -f flask-deployment.yaml


## Check status
kubectl get pods

### U will see pods running


## Port Forward to access
kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0

## Now copy external ip and :5000 and see ur app there....
```

### 6. PROMETHEUS AND GRAFANA MONITORING OF YOUR APP

```bash
## Open another VM terminal 

kubectl create namespace monitoring

kubectl get ns


## Apply Monitoring Configs
kubectl apply -f prometheus/prometheus-configmap.yaml

kubectl apply -f prometheus/prometheus-deployment.yaml

kubectl apply -f grafana/grafana-deployment.yaml

## Check target health also..
## On IP:9090
kubectl port-forward --address 0.0.0.0 svc/prometheus-service -n monitoring 9090:9090

## Username:Pass --> admin:admin123
kubectl port-forward --address 0.0.0.0 svc/grafana-service -n monitoring 3000:3000



## Configure Grafana
# 1. Login (admin/admin123)
# 2. Go to Settings > Data Sources > Add Data Source
# 3. Choose Prometheus
# 4. URL: http://prometheus-service.monitoring.svc.cluster.local:9090
# 5. Click Save & Test
# 6. Green success mesaage shown....


######################################


# Now make a dashboard for different visualization
# See course video for that....
```

### 7. PROJECT STRUCTURE REFERENCE

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
