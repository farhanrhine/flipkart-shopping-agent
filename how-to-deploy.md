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
  - In machine configuration set Machine Type:
    - Series: `E2`
    - Preset: `Standard`
    - Memory: `16 GB RAM`
  - IN a os and storage set Boot Disk:
    - Change size to `256 or 150 GB`
    - Image: Select **Ubuntu 24.04 LTS x86_64 amd64 noble build in 2025-06-06**
    - its charge around $0.15 per hour, which is around $112.84 per month (you can stop the VM when not in use to save costs) . aws charge 2-3 times more for similar configuration, so google cloud is a better choice for this project.
  - Networking on firewall:
    - Enable HTTP and HTTPS traffic and load balancing (this will open ports 80 and 443, we will also open custom ports later for our app and monitoring)
    - enable ip forwarding (important for kubernetes to work properly inside the VM)
    - rest left as default and click **Create** to launch the VM instance. It will take around 1-2 minutes to be fully up and running. You can see the status in the VM instances dashboard. Once it's running,

- **Create the Instance**

- **Connect to the VM**
  - Use the **SSH** option provided to connect to the VM from the browser.
  - click on the SSH button next to your VM instance in the Google Cloud Console. This will open a new browser window with a terminal connected to your VM. You can run commands directly in this terminal to set up your environment and deploy your application.
  - its asked authorize the browser to access your Google Cloud resources, click **Allow** to proceed. This will establish a secure SSH connection to your VM instance, allowing you to manage it from the terminal.
  - type `clear` command to clear the terminal and start with a clean slate.



### 2. Configure VM Instance

- **Install Docker**

  - Search: "Install Docker on Ubuntu"
  - Open the first official Docker website (docs.docker.com)
  - Scroll down and copy the **Install using the apt repository** sectioon  and paste into your VM terminal or click here https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository 

  - copy all latest version commands , specific version will be advanced used case based on project requirements.

  - Then copy  whole command from step 1  and paste the **ssh-in-browser** command, then for step 2, copy and paste the commands to install Docker on your VM.
  - if asked Yes/No, type `Y` and press Enter to confirm the installation.
  - Then run the **step -3 run ** to test Docker:

    ```bash
    sudo docker run hello-world
    
    ```
    - You should see a message confirming that Docker is installed and working correctly. If you see this message, it means Docker is successfully installed on your VM and you can proceed to the next steps of configuring Minikube and deploying your application.

- **Run Docker without sudo**

  - On the same page, scroll to: **"Post-installation steps for Linux"** OR CLICK HERE https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user 
  - Paste all 4 commands one by one to allow Docker without `sudo`
  - Last command is for testing

- **Now Enable some Docker services to start on boot**

  - On the same page, scroll down to: **"Configure Docker to start on boot with systemd"** or click here https://docs.docker.com/engine/install/linux-postinstall/#configure-docker-to-start-on-boot-with-systemd
  - Copy and paste the command block (2 commands):

    ```bash
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    ```
  - basically its automatically starts the Docker service when the VM boots up, so you don't have to manually start it every time.

- **Verify Docker Setup**

  ```bash
  docker --version              # Should show Docker version
  systemctl status docker       # You should see "active (running)"
  docker ps                     # No container should be running
  docker ps -a                 # Should show "hello-world" exited container
  ```

### 3. Configure Minikube inside VM after docker bez its dependency depend upon docker to run the cluster, so we need to install docker first and then minikube. Minikube will use the Docker engine inside the VM to create and manage the Kubernetes cluster.

- **Install Minikube**

  - Open browser and search: `Install Minikube`
  - Open the first official site (https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download) with `minikube start` on it

  - Go installation section Choose:
    - **OS:** Linux
    - **Architecture:** *x86*
    - Release: **Stable**
    - Select **Binary download**
  - Reminder: You have already done this on Windows, so you're familiar with how Minikube works

- **Install Minikube Binary on VM**

  - Copy and paste the 2 installation commands from the website into your VM terminal to download and install Minikube:

    ```bash
    curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64

    sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
    ```

- **Start Minikube Cluster**

  ```bash
  minikube start
  ```
  - this is basically your kubernetes cluster running inside the VM, and it will use Docker to create the necessary containers for the cluster components. You should see output indicating that Minikube is starting and setting up the cluster. This may take a few minutes.

  - This uses Docker internally, which is why Docker was installed first

- **Now Install kubectl**

  - Search: `Install kubectl linux` or click here https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-kubectl-binary-with-curl-on-linux 

  - go to installation section and choose x86 architecture and copy the 1st commands to install kubectl on your VM terminal:
  - Run the first command this  
  ```bash
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  ```


  - Run the second command to validate the download
  ```bash
     curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
  ```

  - Instead of installing manually, go to the **Snap section** (below on the same page) name Install using other package management  bez we using ubuntu and snap is already installed on ubuntu, so we can use snap to install kubectl easily with one command, so copy and paste the snap command to install kubectl  or click here(https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-other-package-management):
  
  - sudo need before snap command because snap needs root permissions to install packages, so make sure to include `sudo` when running the command to install kubectl with snap. The `--classic` flag is used to allow kubectl to access system resources that it needs to function properly, which is necessary for kubectl to work correctly on your VM.

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

  
  - **<span style="color:red;">Important Note</span>**: 
    Update the `prometheus-configmap.yaml` file's `scrape_configs` section to point to your Flask app by replacing `<VM-External-IP>` with your actual external IP address:
    
    ```yaml
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
      
      - job_name: 'flask-app'
        metrics_path: /metrics
        static_configs:
          - targets: ['<VM-External-IP>:5000']  # e.g., ['34.42.228.136:5000']
    ```
    
    **Why this is needed:** Prometheus has two scrape targets:
    - **Target 1** (`localhost:9090`): Prometheus scrapes its own metrics to monitor itself
    - **Target 2** (`<VM-External-IP>:5000`): Prometheus scrapes your Flask app's metrics to monitor the application
    
    Without this configuration, Prometheus won't be able to connect to your Flask app and will report "no targets available". This ensures your application's performance metrics (request count, latency, errors) are properly collected and available for visualization in Grafana.






- **Clone your GitHub repo**

  ```bash
  git clone https://github.com/farhanrhine/flipkart-shopping-agent.git 
  ls
  cd flipkart-shopping-agent
  ls  # You should see the contents of your project
  ```

### 4. Interlink your Github on VSCode and on VM
 - all 3 need to conneted local vscode , github and gcp vm to push code from local to github and then pull it on vm to deploy, so we need to set up git on the VM and connect it to our GitHub account.

```bash
git config --global user.email "mohammadfarhanalam09@gmail.com" # your email
git config --global user.name "farhanrhine" # your github username

git add .
git commit -m "commit"
git push origin main
```

- When prompted:
  - **Username**: `farhanrhine` (your GitHub username)
  - **Password**: GitHub token (paste, it's invisible) not github password, you need to generate a personal access token on GitHub and use it as the password for authentication when pushing from the VM. This is a security measure implemented by GitHub to enhance account security, as they no longer allow direct password authentication for Git operations. Instead, you must use a personal access token, which can be generated in your GitHub account settings under Developer settings → Personal access tokens. Make sure to grant the necessary scopes (like `repo` and `read:packages`) when creating the token, and then copy it to use as the password when prompted during the git push operation from your VM.

  - how to get GitHub token:
    - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
    - Name: `VM Deployment Token`
    - Expiration: `No expiration`
    - Scopes: Check `repo` ,`workflow`, `admin-org`, `admin:repo_hook`, `admin:org_hook` # these scopes are necessary for pushing code and managing repositories from the VM( you can give more based on needs).
    - Click: "Generate token"
    - Copy the generated token (you won't see it again) and use it as the password when pushing from the VM.
    - you see message : everything up to date, it means your code is already pushed to GitHub and you can proceed to pull it on the VM for deployment.
    - now lets say you create new file test.py local in vscode and push on github, then you can pull it on vm with `git pull origin main` command to get the latest code changes before building and deploying your app.
    - this we called version control and it's essential for managing code changes across different environments (local, GitHub, VM) and ensuring that you can easily update and maintain your application as you develop it further.
    - this will same process you will follow for any future code changes, just commit and push from local vscode to GitHub, then pull on VM before building and deploying the updated app.

---

### 5. set up gcp firewall rules to allow traffic on custom ports
- By default, only ports 80 and 443 are open for HTTP and HTTPS traffic. Since our Flask app and monitoring tools will be running on different ports (5000 for Flask, 9090 for Prometheus, and 3000 for Grafana), we need to create custom firewall rules to allow incoming traffic on these ports.

- **Create Firewall Rules:**
  - Go on gcp search firewall choose the VPC network → Firewall rules in the Google Cloud Console.
  - Click on "Create Firewall Rule"
  - Name: `allow-flask-prometheus-grafana` # you can choose any name, just make it descriptive
  - Network: Select the default network (or the one your VM is in)
  - Direction of traffic: Ingress
  - Action on match: Allow
  - Targets: All instances in the network (or specify your VM instance)
  - source filter: IPv4 ranges
  - Source IP ranges: `0.0.0.0/0` (allows traffic from any IP address)
  - in protocols and ports:
    - selected Allow all options bez we need the ports this enable below ports to be accessible from outside the VM:
      - Protocol: TCP, Port: 5000 (for Flask app)
      - Protocol: TCP, Port: 9090 (for Prometheus)
      - Protocol: TCP, Port: 3000 (for Grafana)
  - Click "Create" to save the firewall rule.




### 6. Build and Deploy Your APP on VM (Complete Guide)

**STEP 1: find repo**
go ssh-in-browser:
type `clear` to clear the terminal and start with a clean slate, then follow these steps:
 type `ls` its show github repo folder name `flipkart-shopping-agent` then type `cd flipkart-shopping-agent` to go inside the project folder, then used type `clear` or type `ls` to see the contents of the project, you should see all your project files and folders.

**STEP 2: Point Docker to Minikube**
```bash
eval $(minikube docker-env)
```
- This tells Docker to use Minikube's internal Docker daemon (important!) to build images directly inside the Minikube cluster, so they are immediately available for deployment without needing to push to an external registry.(take some time to execute, wait for it to complete before moving to the next step)

**STEP 3: Build the Docker Image**
```bash
docker build -t flask-app:latest .
```

-  this name i set in the `flask-deployment.yaml` file as the image name for the Flask app container, so it needs to match exactly for Kubernetes to find and deploy the correct image. If you change the image name here, make sure to update it in the deployment file as well(take some time to execute, wait for it to complete before moving to the next step).

- verify the image is built successfully and available in Minikube's Docker registry:
```bash
docker images
```
You should see `flask-app` or `flask-app:latest` in the list of images.


**STEP 4: Create Kubernetes Secrets**
- its need to done inside your github directory inside like this `flipkart-shopping-agent` because we need to use the credentials from the `.env` file which is in the root of the project, so make sure to navigate to the project directory before running the command to create secrets.

- Replace `"..."` with your actual credentials from AstraDB, Groq, and HuggingFace:

```bash
kubectl create secret generic flipkart-secrets \
  --from-literal=ASTRA_DB_API_ENDPOINT="https://your-astradb-endpoint..." \
  --from-literal=ASTRA_DB_APPLICATION_TOKEN="your-token-here..." \
  --from-literal=ASTRA_DB_KEYSPACE="flipkart" \
  --from-literal=GROQ_API_KEY="your-groq-key..." \
  --from-literal=HUGGINGFACEHUB_API_TOKEN="your-huggingface-token..."
```
- like this you are securely storing all your sensitive credentials in Kubernetes secrets, which can then be accessed by your Flask app without hardcoding them in the code or configuration files. This is a best practice for managing sensitive information in a Kubernetes environment.

- its messages secret/flipkart-secrets created, it means the secrets are successfully created in Kubernetes and you can proceed to deploy your application which will use these secrets to access the necessary services (AstraDB, Groq, HuggingFace) securely.


**STEP 5: Deploy All Services (Order Matters!)**
- its need to done in your github directory inside like this `flipkart-shopping-agent` because we need to use the deployment files which are in the root of the project, so make sure to navigate to the project directory before running the command to deploy the services.
# 1. Deploy Flask App

```bash
kubectl apply -f flask-deployment.yaml # the file name can be different based on what you named it, just make sure to use the correct file name for your Flask app deployment
- its message like "deployment.apps/flask-app created" it means the Flask app deployment is successfully created in Kubernetes and you can proceed to deploy the monitoring components (Prometheus and Grafana) to monitor your application.

# verify Flask app is running
kubectl get pods
# You should see a pod with the name "flask-app" and its status should be "Running". If it's not running, you can check the logs with:
kubectl logs <flask-app-pod-name>
```

- currently my application is running inside the kubernetes cluster which is running inside the VM, so to access the application from outside (like from your local machine or browser), we will use port forwarding to forward the ports from the cluster to the VM, and then we have already set up firewall rules to allow traffic on those ports, so you can access the application and monitoring tools using the VM's `external IP` address and the respective ports.

- used this command to check the `external IP` of your VM instance, which you will use to access your Flask app, Prometheus, and Grafana from your local machine or browser:

```bash
kubectl port-forward svc/flask-service 5000:80 --address 0.0.0.0
```
-  the flask-service name i set in the `flask-deployment.yaml` file as the service name for the Flask app, so it needs to match exactly for Kubernetes to forward the correct service ports. If you change the service name in the deployment file, make sure to update it here as well.
- why `--address 0.0.0.0`? This allows the port forwarding to accept connections from any IP address, which is necessary for accessing the service from outside the VM (like from your local machine or browser). Without this flag, the port forwarding would only accept connections from localhost (the VM itself), and you wouldn't be able to access it externally.

- now you can open a new terminal window (keep the port forwarding running in the first terminal) and run the following command to forward Prometheus port:

- you see message like "Forwarding from 0.0.0.0 -> 5000" it means the port forwarding is successfully set up and you can now access your Flask app using the VM's external IP address and port 5000 (e.g., `http://<VM-External-IP>:5000`).

- if you get error  then check firewall rules and make sure you have allowed traffic on port 5000, also check the pod status and logs to ensure the Flask app is running correctly.


<span style="color:red;">============ till here you have successfully deployed your Flask app and set up port forwarding to access it externally. Now let's deploy the monitoring components (Prometheus and Grafana) to monitor your application. ============</span>

```bash

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
