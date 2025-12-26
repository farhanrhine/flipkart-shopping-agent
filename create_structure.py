"""
📦 FLIPKART Product Recommender - Project Structure Generator

Run this script to create the folder & file structure
derived from the GitHub repository tree (structure-only).

Usage:
    python create_structure.py
"""

import os

# -----------------------------
# Directories to create
# -----------------------------
structure = [
    "data",
    "flipkart",
    "grafana",
    "prometheus",
    "static",
    "templates",
    "utils",
]

# -----------------------------
# Files to create (empty)
# -----------------------------
files = [
    # Root
    ".gitignore",
    "Dockerfile",
    "FULL DOCUMENTATION.md",
    "app.py",
    "flask-deployment.yaml",
    "requirements.txt",
    "setup.py",

    # Data
    "data/flipkart_product_review.csv",

    # Flipkart package
    "flipkart/__init__.py",
    "flipkart/config.py",
    "flipkart/data_converter.py",
    "flipkart/data_ingestion.py",
    "flipkart/rag_chain.py",

    # Grafana
    "grafana/grafana-deployment.yaml",

    # Prometheus
    "prometheus/prometheus-configmap.yaml",
    "prometheus/prometheus-deployment.yaml",

    # Static & templates
    "static/style.css",
    "templates/index.html",

    # Utils
    "utils/__init__.py",
    "utils/custom_exception.py",
    "utils/logger.py",
]

# -----------------------------
# Generator
# -----------------------------
def create_structure():
    print("📦 Creating Flipkart Recommender project structure...\n")

    for path in structure:
        os.makedirs(path, exist_ok=True)
        print(f"📁 Created: {path}/")

    print()

    for f in files:
        parent = os.path.dirname(f)
        if parent:
            os.makedirs(parent, exist_ok=True)

        if not os.path.exists(f):
            with open(f, "w"):
                pass
            print(f"📄 Created: {f}")
        else:
            print(f"⏭️  Skipped: {f}")

    print("\n✅ Project structure created successfully!")
    print("Next: start filling logic where needed 🔥")


if __name__ == "__main__":
    create_structure()
