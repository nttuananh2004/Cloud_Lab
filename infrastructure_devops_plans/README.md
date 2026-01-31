# Infrastructure and DevOps Strategy

## Architectural Decision Record (ADR)
**Context:** The current portfolio project operates under a personal budget with variable traffic patterns.
**Decision:** I have implemented a dual-strategy approach to balance immediate cost-efficiency with future scalability.

1.  **Production Environment (Current):**
    * **Architecture:** Serverless (AWS Lambda).
    * **Deployment Method:** Zip-based deployment via GitHub Actions.
    * **Justification:** This adheres to the **Cost Optimization** pillar of the AWS Well-Architected Framework. For current workloads, a serverless approach ensures $0 operational cost (Free Tier) and lowest possible latency (no container cold starts).

2.  **Enterprise Readiness (Planned):**
    * **Architecture:** Microservices on Kubernetes (Amazon EKS).
    * **Deployment Method:** Containerized (Docker) orchestrated by Helm.
    * **Justification:** This directory contains the Infrastructure-as-Code (IaC) artifacts required to migrate the system when traffic demands horizontal scaling and high availability.

## Technical Comparison

| Feature | Current Implementation (Portfolio Mode) | Enterprise Target (Migration Plan) |
| :--- | :--- | :--- |
| **Compute Engine** | AWS Lambda (Python Runtime) | Amazon EKS (Kubernetes) |
| **Artifact Type** | Raw Source Code (.zip) | Docker Container Images |
| **Orchestration** | None (Event-driven) | K8s Deployment & Service |
| **Cost Model** | Pay-per-request (FinOps Optimized) | Provisioned Capacity (Performance Optimized) |

## Repository Artifacts

This directory hosts the blueprints for the Enterprise Target architecture.

### 1. Containerization Strategy (/docker_containerization)
* **Base Image:** `public.ecr.aws/lambda/python:3.12`
* **Goal:** Standardize the execution environment to eliminate "works on my machine" discrepancies between development and production.

### 2. Orchestration Manifests (/kubernetes_orchestration)
* **Resource:** `Deployment`
* **Configuration:**
    * **Replicas:** 3 (High Availability).
    * **Resource Quotas:** Defined CPU/Memory limits to prevent noisy neighbor issues.
    * **Health Checks:** Liveness and Readiness probes configured.

### 3. Package Management (/helm_charts)
* **Tool:** Helm v3
* **Goal:** abstracting complexity and enabling version-controlled infrastructure deployments.

## Pilot Migration Strategy
The **NetProbe** module has been selected as the **Pilot Service** (Proof of Concept) for this migration initiative. 

* **Rationale:** NetProbe represents a stateless workload suitable for containerization.
* **Execution:** Upon successful validation of these artifacts on a staging cluster, this pattern will be replicated for `SOS_Broadcast` and `Face_Comparison` modules.