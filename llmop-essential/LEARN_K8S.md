# 🎓 Learning Kubernetes Check YAML (The "Vibe" Way)

You used AI to generate the YAML, but understanding it is actually pretty simple! Think of Kubernetes (K8s) like managing a **restaurant**.

Here is your project broken down into plain English, starting from the Recipe (Docker) to the Restaurant (Kubernetes).

---

## PART 1: The Dockerfile (The Recipe) 📜

Before Kubernetes can serve your food, you need a recipe to make it. That's the **Dockerfile**. It tells the computer how to build your app from scratch.

```dockerfile
# 1. THE BASE (The Ingredients) 🥦
FROM python:3.12-slim    # Start with a lightweight version of Python (like buying pre-made dough)

# 2. THE SETUP (The Prep Station) 🔪
WORKDIR /app             # Create a folder called '/app' and stand inside it.

# 3. THE UTENSILS (Installing Tools) 🛠️
RUN pip install uv       # Install 'uv' (a super fast tool installer)

# 4. THE RECIPE (Dependencies) 📖
COPY pyproject.toml .    # Copy the ingredient list from your computer to the container
RUN uv pip install ...   # Install all the libraries (Flask, LangChain, etc.)

# 5. THE MAIN COURSE (The Code) 🥘
COPY . .                 # Copy ALL your files (app.py, src/, etc.) into the container

# 6. THE SERVING PLATE (Exposing Ports) 🍽️
EXPOSE 5000              # Open port 5000 so people can talk to the app

# 7. SERVE IT! (The Command) 🔔
CMD ["python", "app.py"] # When the container starts, run this command to serve the app!
```

---

## PART 2: The Deployment (The Kitchen Staff) 👨‍🍳

Now that we have the recipe (Image), the **Deployment** tells K8s *how many* cooks (Pods) we need to cook it.

```yaml
apiVersion: apps/v1        # 🏷️ Version of the K8s API we are using
kind: Deployment           # 📝 Type of document: This is a DEPLOYMENT
metadata:
  name: flask-app          # 📛 The name we give this manager
```

### The Specs (The Instructions)

```yaml
spec:
  replicas: 1              # 1️⃣ We want EXACTLY 1 copy of this app running.
                           # If it crashes, K8s starts a new one to keep this at 1.
  
  selector:                # 🎯 How the manager finds its workers.
    matchLabels:           # "I manage any pod wearing a 'flask' name tag"
      app: flask
```

### The Template (The Cookie Cutter) 🍪

This describes the actual **Pod** (container) that gets created effectively "Run the Docker Recipe here".

```yaml
  template:
    metadata:
      labels:              # 🏷️ Giving the worker a name tag so the manager finds it
        app: flask
    spec:
      containers:
      - name: flask-container    # 📦 Name of the container
        image: flask-app:latest  # 🖼️ The Docker image to use (built from Part 1)
        
        imagePullPolicy: IfNotPresent # ⚡ Optimization: "If you have the image locally, don't download it again"
        
        ports:
          - containerPort: 5000  # 🚪 The app listens on this door number inside the container
        
        envFrom:                 # 🔑 Give the app the secrets (API keys)
          - secretRef:
              name: flipkart-secrets
```

---

## PART 3: The Service (The Waiter/Receptionist) 🤵

The **Service** is the stable public face. Pods die and get replaced (changing IP addresses), but the Service stays at the same address and forwards traffic to whatever Pods are currently alive.

```yaml
apiVersion: v1
kind: Service              # 📝 Type of document: This is a SERVICE
metadata:
  name: flask-service      # 📛 Name of the service
```

### Routing Rules 🔀

```yaml
spec:
  type: LoadBalancer       # ⚖️ Gives you an external IP address so the world can call you
  
  selector:                # 🎯 Who do I send food (traffic) to?
    app: flask             # "Send traffic to any pod with the 'flask' tag"
  
  ports:
    - protocol: TCP
      port: 80             # 🌐 The Public Door: Users visit port 80 (standard HTTP)
      targetPort: 5000     # 🚪 The Private Door: Traffic is forwarded to port 5000 on the container
```

---

## PART 4: Prometheus (The Health Inspector) 🩺

Prometheus is like a health inspector that walks around checking if everyone is okay. It constantly asks your app: *"Are you healthy? How many requests have you served today?"*

### 1. The Checklist (ConfigMap) 📋

The **ConfigMap** (`prometheus-configmap.yaml`) is the inspector's clipboard. It tells them *who* to check and *how often*.

```yaml
kind: ConfigMap
data:
  prometheus.yml: |
    scrape_interval: 15s        # Check everyone every 15 seconds
    static_configs:
      - targets: ['localhost:9090'] # Check myself
      - targets: ['flask-service...'] # Check the Flask app
```

### 2. The Security Pass (RBAC) 💳

To check on everyone, the inspector needs a badge. That's **RBAC (Role-Based Access Control)** normally found at the bottom of `prometheus-deployment.yaml`.

- **ServiceAccount**: The ID badge/User.
- **ClusterRole**: The permissions (Can access "pods", "nodes", "services").
- **ClusterRoleBinding**: Glueing the badge to the permissions.

### 3. The Deployment

Just like your Flask app, Prometheus itself needs a deployment to run! It's just another container.

---

## PART 5: Grafana (The TV Screen) 📺

Prometheus collects the numbers (The Health Inspector), but **Grafana** makes them look pretty on a TV screen (Dashboards).

### The Visualization Deployment (`grafana-deployment.yaml`)

```yaml
containers:
- name: grafana
  image: grafana/grafana:latest
  env:
    - name: GF_SECURITY_ADMIN_PASSWORD  # 🔑 Setting the default login password
      value: "admin123"
```

It connects to Prometheus, pulls the data, and draws charts like "Requests per second" or "Error Rate".

---

## 🧠 Quick Cheat Sheet

| YAML/Docker Word | What it means in English |
| :--- | :--- |
| **FROM** | Which OS/Language to start with (Windows? Ubuntu? Python?). |
| **WORKDIR** | "cd" into this folder. |
| **COPY** | Copy files from *your* computer to the *container*. |
| **CMD** | The command that runs your app. |
| **kind** | What type of thing am I building? |
| **metadata** | Names and labels for the thing. |
| **spec** | The specific details of what you want. |
| **ConfigMap** | A file full of variables/settings (like a `.env` file but for K8s). |
| **RBAC** | Security rules. "Who is allowed to do what?" |

---

## 🛠️ The Ultimate "Copy-Paste" Template (For Future You) 🔮

Building a new project? Just copy this block and fill in the `[BRACKETS]`.

```yaml
# 1. THE DEPLOYMENT (Run the App)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: [YOUR-APP-NAME]       # e.g., my-cool-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: [YOUR-APP-LABEL]   # e.g., cool-app
  template:
    metadata:
      labels:
        app: [YOUR-APP-LABEL] # MUST match the one above
    spec:
      containers:
      - name: [CONTAINER-NAME]
        image: [YOUR-IMAGE]:latest
        ports:
          - containerPort: [INTERNAL-PORT]  # e.g., 5000 (Flask), 3000 (Node), 8000 (FastAPI)
---
# 2. THE SERVICE (Expose the App)
apiVersion: v1
kind: Service
metadata:
  name: [YOUR-SERVICE-NAME]
spec:
  type: LoadBalancer
  selector:
    app: [YOUR-APP-LABEL]     # MUST match the labels in Deployment
  ports:
    - port: 80                # The port the world sees (keep as 80 usually)
      targetPort: [INTERNAL-PORT] # The port your app runs on (same as above)
```

## 🚀 How to Learn More?

1. **Play with it**: Change `replicas: 1` to `replicas: 3`, apply it, and watch 3 pods appear!
2. **Break it**: Delete a line and see what error `kubectl` gives you. It's the best way to learn.
3. **Read the Docs**: The [Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/) tutorial is actually surprisingly good and interactive.
