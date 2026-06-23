# DevOps Reboot Learn

A small polyglot microservices playground for learning Docker networking and API gateway routing — **without Eureka or a service registry**.

## Architecture

```
Client
  ↓
Kong API Gateway (:8000)
  ↓
┌─────────────────────────────────────────────────────┐
│  auth-service        Spring Boot      :8080       │
│  user-service        NestJS           :3000       │
│  inventory-service   Node.js/Express  :3001       │
│  analytics-service   Django           :8000       │
└─────────────────────────────────────────────────────┘
  ↓
PostgreSQL + Redis (shared infrastructure)
```

Services talk to each other using **Docker DNS names** (e.g. `http://auth-service:8080`). Kong routes external traffic by path prefix.

| Gateway path   | Backend service      | Example                          |
|----------------|----------------------|----------------------------------|
| `/auth/*`      | auth-service:8080    | `POST /auth/login`               |
| `/users/*`     | user-service:3000  | `GET /users`                     |
| `/inventory/*` | inventory-service:3001 | `GET /inventory`             |
| `/analytics/*` | analytics-service:8000 | `GET /analytics`             |

## Why no Eureka?

Eureka is tightly coupled to the Spring ecosystem. In a mixed stack (Spring Boot, NestJS, Node.js, Django), each non-Spring service would need custom registration logic.

For a learning setup with a fixed number of containers, **static Docker DNS + Kong** is simpler and enough:

- Docker resolves service names automatically on the `app-network` bridge
- Kong declaratively routes `/auth`, `/users`, `/inventory`, `/analytics` to the right backend
- No dynamic service discovery needed until you scale to many instances across many hosts

When you outgrow this pattern (~50+ dynamic instances), consider **Consul** or **Kubernetes** built-in service discovery.

## Quick start

```bash
docker compose up --build
```

Wait until all health checks pass, then try:

```bash
# Health checks through Kong
curl http://localhost:8000/auth/health
curl http://localhost:8000/users/health
curl http://localhost:8000/inventory/health
curl http://localhost:8000/analytics/health

# Sample API calls
curl http://localhost:8000/users
curl http://localhost:8000/inventory
curl http://localhost:8000/analytics
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret"}'
```

Kong Admin API (for debugging routes): `http://localhost:8001`

## Monitoring & control (UI)

All monitoring tools start with the normal `docker compose up` command.

| Tool | URL | Purpose |
|------|-----|---------|
| **Portainer** | http://localhost:9000 | Start/stop containers, view logs, CPU/RAM, exec into shells |
| **Uptime Kuma** | http://localhost:3002 | Uptime history, downtime alerts, status pages |
| **Grafana** | http://localhost:3003 | Dashboards (login: `admin` / `admin`) |
| **Prometheus** | http://localhost:9090 | Raw metrics & query explorer |
| **cAdvisor** | http://localhost:8081 | Per-container resource usage |

### What each UI is for

**Portainer** — day-to-day container control. See all 11 containers, restart a crashed service, tail logs, check health status. First visit: create an admin account, then pick **Local** Docker environment.

**Uptime Kuma** — downtime tracking. On first visit, create an account, then add HTTP monitors for your endpoints.

**Option A — UI (single monitor, e.g. auth-service):**

1. Open http://localhost:3002 and log in.
2. Click **+ Add New Monitor**.
3. Choose **HTTP(s)**.
4. Set **Friendly Name** to `Kong / Auth` (or `Auth Service (direct)`).
5. Set **URL** to `http://kong:8000/auth/health` (via gateway) or `http://auth-service:8080/health` (direct).
6. Leave interval at 60s, then **Save**.

Use Docker service hostnames (`kong`, `auth-service`, …) because Uptime Kuma runs on the same `app-network`.

**Option B — seed all monitors from config:**

```bash
pip install -r scripts/requirements-uptime-kuma.txt
UPTIME_KUMA_USERNAME=admin UPTIME_KUMA_PASSWORD=yourpassword \
  python scripts/seed-uptime-kuma.py
```

Monitors are defined in `monitoring/uptime-kuma/monitors.yaml`.

| Monitor name | URL (from Uptime Kuma container) |
|--------------|----------------------------------|
| Kong / Auth | http://kong:8000/auth/health |
| Kong / Users | http://kong:8000/users/health |
| Kong / Inventory | http://kong:8000/inventory/health |
| Kong / Analytics | http://kong:8000/analytics/health |
| Auth Service (direct) | http://auth-service:8080/health |
| User Service (direct) | http://user-service:3000/health |
| Inventory Service (direct) | http://inventory-service:3001/health |
| Analytics Service (direct) | http://analytics-service:8000/health |

From your host (outside Docker), use `http://localhost:8000/auth/health` instead.

Try stopping a service to see downtime recorded:

```bash
docker compose stop user-service
# Uptime Kuma and Grafana will show it as down within ~15s
docker compose start user-service
```

**Grafana** — pre-provisioned **Service Uptime** dashboard (Prometheus blackbox probes every 15s). Explore → query `probe_success` to see 1 = up, 0 = down.

**Prometheus** — for learning PromQL. Example: `probe_success{instance=~".*users.*"}`

### Simulate downtime (learning exercise)

```bash
# Stop one backend
docker compose stop inventory-service

# Watch via CLI
docker compose ps
curl -s http://localhost:8000/inventory/health || echo "gateway route failed"

# Bring it back
docker compose start inventory-service
```

## Project layout

```
.
├── docker-compose.yml          # All services + Kong + Postgres + Redis
├── kong/kong.yml               # Declarative Kong routes (DB-less mode)
├── monitoring/                 # Prometheus, Grafana, blackbox probes
└── services/
    ├── auth-service/           # Spring Boot
    ├── user-service/           # NestJS
    ├── inventory-service/      # Express
    └── analytics-service/      # Django
```

## Running a single service locally

Each service can run outside Docker for development. Start Postgres and Redis first:

```bash
docker compose up postgres redis -d
```

Then run the service from its directory (see each service's stack-specific commands).

## Next steps for learning

1. Add a Kong plugin (rate limiting, JWT, CORS)
2. Add inter-service HTTP calls using Docker DNS names
3. Wire services to PostgreSQL with real models/migrations
4. Add a simple frontend that calls Kong on port 8000
5. Compare this setup with Consul-based discovery or Kubernetes Services
6. Add Uptime Kuma notification channels (email, Slack, Discord)
7. Build Grafana alerts on `probe_success == 0`
