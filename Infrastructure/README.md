# Infrastructure and DevOps Strategy

## Architectural Decision Record (ADR)
**Context:** The current portfolio project operates under a personal budget with variable traffic patterns.
**Decision:** I have implemented a dual-strategy approach to balance immediate cost-efficiency with future scalability.

1.  **Production Environment (Current):**
    * **Architecture:** Serverless (AWS Lambda).
    * **Justification:** Adheres to the **Cost Optimization** pillar of the AWS Well-Architected Framework ($0 operational cost, Zero-idle compute).

2.  **Hybrid Lab / Staging (Current Testing):**
    * **Architecture:** Containerized Microservices hosted on AWS EC2.
    * **Deployment:** Provisioned via **Terraform (IaC)** and orchestrated by **Docker-Compose**.
    * **Justification:** Allows for rigorous integration testing of containerized logic without the overhead of a full Kubernetes cluster.

3.  **Enterprise Readiness (Planned Target):**
    * **Architecture:** Microservices on Kubernetes (Amazon EKS).
    * **Justification:** Blueprint artifacts ready for seamless migration when traffic demands horizontal scaling (HPA) and Self-healing.

---

## 🛠 SRE Runbook: Infrastructure Cheat Sheet
*A quick reference guide for deploying the Hybrid Lab topology.*

### 1. Terraform (Infrastructure Provisioning)
Navigate to the `/infrastructure` directory to provision the AWS EC2 instance:
* `terraform init` - Initializes the backend and downloads the AWS provider.
* `terraform plan` - Previews the infrastructure changes (Security Groups, EC2).
* `terraform apply -auto-approve` - Executes the build plan.
* `terraform destroy` - **[FINOPS]** Tears down the infrastructure to prevent billing.

### 2. Docker Compose (Microservices Orchestration)
Once SSH'd into the EC2 instance (or running locally), manage the application stack:
* `docker-compose up -d --build` - Builds the images and starts containers in detached mode.
* `docker-compose logs -f` - Tails the consolidated logs for all 3 microservices (NetProbe, FaceAuth, SOS).
* `docker-compose down` - Stops and removes containers, networks, and volumes.

---

## Repository Artifacts
* `/infrastructure/main.tf`: The declarative AWS environment blueprint.
* `/infrastructure/docker/`: Standardized Python 3.9-slim execution environments.
* `/infrastructure/kubernetes_orchestration/`: EKS-ready `Deployment.yaml` featuring 3 Replicas and strict `128Mi/250m` Resource Quotas to prevent OOM errors.
