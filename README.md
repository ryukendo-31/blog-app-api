# Blog API --- FastAPI, Docker & CI/CD

A REST API built with **FastAPI** and **PostgreSQL**, containerized with
**Docker**, and automatically tested and deployed to an **Oracle Cloud
VM** using **GitHub Actions**.

## Overview

This project demonstrates an end-to-end backend deployment workflow:

1.  Develop and test a FastAPI application.
2.  Package the application as a Docker image.
3.  Build images for both `linux/amd64` and `linux/arm64`.
4.  Push images to Docker Hub.
5.  Deploy the latest image to an Oracle Cloud VM through SSH and Docker
    Compose.

The deployed architecture runs the API in Docker while PostgreSQL
remains installed as a service on the VM host.

## Tech Stack

-   **Backend:** Python, FastAPI
-   **Application server:** Gunicorn with Uvicorn workers
-   **Database:** PostgreSQL
-   **ORM / validation:** SQLAlchemy, Pydantic
-   **Authentication:** OAuth2 password flow and JWT
-   **Containerization:** Docker, Docker Compose
-   **CI/CD:** GitHub Actions
-   **Image registry:** Docker Hub
-   **Deployment target:** Oracle Cloud VM (Ubuntu, ARM64)

## Features

-   User registration and user retrieval
-   Post creation and retrieval
-   JWT-based authentication
-   Vote functionality for posts
-   PostgreSQL persistence
-   Interactive API documentation through Swagger UI
-   Automated tests with `pytest`
-   Multi-platform Docker image builds
-   Automatic deployment on pushes to `main`

> For the exact request/response schemas and available routes, run the
> application and open `/docs`.

## Project Structure

The application source is organized under `app/`. A typical structure
for this project is:

``` text
blog-app-api/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── posts.py
│   │   ├── users.py
│   │   └── vote.py
│   ├── ...
├── tests/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

The exact files may vary as the project evolves.

## Run Locally

### 1. Clone the repository

``` bash
git clone https://github.com/ryukendo-31/blog-app-api.git
cd blog-app-api
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the location expected by the application
settings. Do not commit this file.

Example values (replace placeholders with your own local configuration):

``` env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=YOUR_LOCAL_DATABASE_PASSWORD

SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Make sure PostgreSQL is running and the database named in
`DATABASE_NAME` exists.

### 5. Start the API

Use the command appropriate for your project's application entry point.
For the deployment configuration used in this project:

``` bash
uvicorn app.main:app --reload
```

Open:

-   Swagger UI: `http://localhost:8000/docs`
-   OpenAPI schema: `http://localhost:8000/openapi.json`

## Run Tests

Configure a test database and the required environment variables, then
run:

``` bash
pytest -v
```

The GitHub Actions workflow starts a temporary PostgreSQL service for
the test job and supplies test-only environment variables. These are
separate from the production database.

## Docker

### Build the image locally

``` bash
docker build -t blog-app .
```

### Run the container

The application needs its environment variables and database
connectivity. For example, when the database is reachable from the
Docker host:

``` bash
docker run --rm \
  --name blog-api \
  --network host \
  --env-file .env \
  blog-app
```

The production VM uses host networking because the application connects
to PostgreSQL on the VM through `localhost`. Host networking behavior
differs by operating system; this deployment configuration is intended
for the Linux VM.

## Production Deployment

The production deployment uses:

-   Docker image: `aaryan31/blog-app:latest`
-   Docker Compose file on the VM:
    `/home/aaryan/docker-compose.prod.yml`
-   Environment file on the VM: `/home/aaryan/.env`
-   API port: `8000`
-   PostgreSQL: installed and managed directly on the VM host

The production Compose configuration manages **only the API**. It does
not create or manage a PostgreSQL container.

Useful commands on the VM:

``` bash
# Check the API container
docker ps --filter name=blog-api

# View application logs
docker logs --tail 50 blog-api

# Check the API locally on the VM
curl -I http://localhost:8000/docs

# Pull the latest API image
docker compose -f /home/aaryan/docker-compose.prod.yml pull api

# Apply the Compose configuration
docker compose -f /home/aaryan/docker-compose.prod.yml up -d
```

## CI/CD Pipeline

Workflow file: `.github/workflows/ci-cd.yml`

The workflow runs on pushes to `main` and pull requests targeting
`main`.

### Job 1: `test-and-push`

-   Checks out the repository.
-   Sets up Python and installs dependencies.
-   Starts a PostgreSQL service for automated tests.
-   Runs `pytest -v`.
-   On pushes to `main`, configures QEMU and Docker Buildx.
-   Logs in to Docker Hub using GitHub repository secrets.
-   Builds and pushes multi-platform images.

Published tags:

``` text
aaryan31/blog-app:latest
aaryan31/blog-app:sha-<commit-sha>
```

### Job 2: `deploy`

The deploy job runs only for pushes to `main` and only after
`test-and-push` succeeds.

It connects to the Oracle VM over SSH, then runs Docker Compose commands
to pull and recreate the API container.

### GitHub Actions Secrets

Configure these under **Repository → Settings → Secrets and variables →
Actions**:

  Secret                 Purpose
  ---------------------- -----------------------------------------
  `DOCKERHUB_USERNAME`   Docker Hub username
  `DOCKERHUB_TOKEN`      Docker Hub access token
  `VM_HOST`              VM public IP or hostname
  `VM_USER`              SSH deployment username
  `VM_SSH_KEY`           Private SSH key for the deployment user

Never commit private keys, `.env` files, database passwords, or JWT
secrets to the repository.

## Deployment Flow

``` text
Push to main
    |
    v
GitHub Actions
    |
    v
Run tests against temporary PostgreSQL
    |
    +---- tests fail ----> Stop; do not deploy
    |
    v
Build AMD64 + ARM64 Docker images
    |
    v
Push images to Docker Hub
    |
    v
SSH into Oracle Cloud VM
    |
    v
Pull latest image with Docker Compose
    |
    v
Recreate API container
    |
    v
Verify API is responding
```

## Important Deployment Notes

-   The VM is ARM64, so the workflow publishes an ARM64 image as well as
    AMD64.
-   PostgreSQL runs on the VM host; the API container uses host
    networking to reach it through `localhost`.
-   The old host-level Gunicorn service is disabled to prevent it from
    competing for port `8000`.
-   Docker is enabled at boot, and the API container uses the
    `unless-stopped` restart policy.
-   A successful CI/CD run means the workflow completed; check the
    container and `/docs` endpoint to verify the application is healthy.

## Security Notes

This is a learning project and the deployment is not a complete
production-hardening setup.

-   Use unique, strong credentials and rotate any credentials that may
    have been exposed.
-   Keep secrets in environment files or GitHub Secrets, never in source
    control.
-   Restrict VM ingress rules to the ports and sources you need.
-   The Docker group grants powerful, effectively root-level access;
    only trusted users should belong to it.
-   Consider a dedicated least-privilege PostgreSQL user instead of
    using a database superuser.
-   Do not share output from commands that print resolved environment
    variables, such as `docker compose config`.

## Future Improvements

-   Add health checks and deployment rollback handling.
-   Use a dedicated, least-privilege database user.
-   Add structured logging and monitoring.
-   Put the API behind a reverse proxy with HTTPS.
-   Add database migrations and a backup strategy.
-   Use immutable image tags (commit SHA) for controlled rollbacks.

## Author

**Aaryan Sharma**

Repository:
[ryukendo-31/blog-app-api](https://github.com/ryukendo-31/blog-app-api)
