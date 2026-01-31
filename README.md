# CLOUD LAB: ENTERPRISE-GRADE AWS INFRASTRUCTURE POC

> This repository serves as a centralized showcase for cloud-native solutions, focusing on **Serverless Orchestration**, **Automated Biometric Analysis**, and **Distributed Network Diagnostics**. All infrastructures follow the **AWS Well-Architected Framework** with a strict focus on Security (PoLP) and Cost-Optimization (FinOps).

---

## TECHNICAL ENVIRONMENT

* **Primary Region:** `ap-southeast-1` (Singapore)
* **Architecture Pattern:** Pure Serverless (Zero-idle cost) & Event-Driven
* **Compliance:** Regional Data Residency & Principle of Least Privilege
* **CI/CD:** GitHub Actions (Automated Pipeline)

---

## MODULE 1: NET_PROBE
### Distributed Network Diagnostic and Geo-Auditing Engine

A serverless utility designed for **real-time network latency analysis** and geographic auditing of target endpoints.

### Architecture Diagram
![NET_PROBE Architecture](assets/Net_probe.png)

### Architecture Highlights
* **Ingestion Layer:** RESTful interface managed by **AWS API Gateway** to receive diagnostic metadata.
* **Compute & Egress:** **AWS Lambda** executes non-blocking ICMP/TCP probes, traversing the regional network boundary to reach external global targets.
* **Persistence:** **Amazon DynamoDB** stores historical logs with an active **TTL (Time To Live)** policy for automated data lifecycle management.

---

## MODULE 2: FACE_BIOMETRIC
### AI-Enhanced Biometric Intelligence Pipeline

An experimental biometric verification system integrating **Computer Vision** and **Large Language Models (LLMs)** for automated identity risk assessment.

### Architecture Diagram
![FACE_BIOMETRIC Architecture](assets/face_biometric.png)

### Architecture Highlights
* **Entry Point:** **AWS API Gateway** ingests base64-encoded image payloads directly to the processing layer.
* **Orchestration:** **AWS Lambda** performs runtime format normalization and coordinates concurrent calls to downstream AI services.
* **Computer Vision:** **Amazon Rekognition** executes facial vector extraction and similarity matching.
* **Intelligence Layer:** **Amazon Bedrock (Claude 3 Haiku)** synthesizes raw biometric metadata into human-readable security reports.

---

## MODULE 3: SOS_BEACON
### Tactical Emergency Uplink & Geo-Spatial Messaging System

A critical response mechanism designed to leverage client-side telemetry for immediate extraction protocols. It bridges the gap between physical location data and cloud-native notification pipelines.

### Architecture Diagram
![SOS_BEACON Architecture](assets/sos.png)

### Architecture Highlights
* **Telemetry Acquisition:** Leverages **HTML5 Geolocation API** for high-precision coordinate capture (Latitude/Longitude) directly from the client browser.
* **Event Ingestion:** **AWS API Gateway** provides a secure, low-latency webhook for distress signal transmission.
* **Logic & Formatting:** **AWS Lambda** processes the payload, validates coordinates, and generates tactical map visualizations (Google Maps deep-linking).
* **Broadcast Layer:** **Amazon SNS** executes a "Fan-out" pattern to instantly broadcast alerts to administrators via Email/SMS with near-zero latency.

---

## 🚀 ENTERPRISE MIGRATION STRATEGY (DEVOPS ROADMAP)

> **Architectural Note:** While the production environment utilizes a **Serverless Zip-based** architecture for maximum cost-efficiency ($0 operational cost), this repository includes a complete **Cloud-Native Migration Plan** for enterprise scaling.

Explore the **[infrastructure_devops_plans](./infrastructure_devops_plans)** directory to view the engineered artifacts for:

* 🐳 **Containerization:** Docker Strategy for standardizing runtime environments.
* ☸️ **Orchestration:** Kubernetes (EKS) Manifests for High-Availability deployment.
* ⚓ **Packaging:** Helm Charts for version-controlled infrastructure scaling.

---

## REPOSITORY STRUCTURE

* `assets/`: High-fidelity AWS infrastructure diagrams.
* `backend/`: Production-ready Lambda source code (Python 3.x).
* `infrastructure_devops_plans/`: **[NEW]** IaC Blueprints for Docker, Kubernetes, and Helm.
* `.github/workflows/`: CI/CD Pipelines for automated deployment.
* `index.html`: Web-based interface for live module demonstration.

---
```bash
STATUS: SYSTEM_READY // REGION: AP-SOUTHEAST-1 // ENGINEER: NGUYEN TRAN TUAN ANH