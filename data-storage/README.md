# Elasticsearch in Docker – Configuration Notes

This document captures the current configuration of Elasticsearch running inside a Docker container. It serves as a reference for how the setup was done.

---

## 1. Memory (RAM)

2 GB of RAM allocated to Elasticsearch (on a server with 8 GB RAM):

```yaml
ES_JAVA_OPTS: -Xms2g -Xmx2g
```

---

## 2. System Setting: `vm.max_map_count`

On the **host** system (not inside the container), this was configured:

```bash
sudo sysctl -w vm.max_map_count=262144
```

Made persistent via:

```bash
echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-elastic.conf
sudo sysctl --system
```

---

## 3. File Descriptors and Memory Lock

In `docker-compose.yml`, under the `data-storage` service:

```yaml
ulimits:
  nofile:
    soft: 65536
    hard: 65536
  memlock:
    soft: -1
    hard: -1
```

---

## 4. Disk Space

Elasticsearch may stop indexing if disk space runs low. The rule is to always keep **10–15% of disk space free**.

---

## 5. Single-Node Mode

Configured with:

```yaml
discovery.type: single-node
```

Elasticsearch runs as a single node — suitable for development/testing, **not** highly available.

---

## 6. Security

Security features were disabled:

```yaml
xpack.security.enabled: "false"
```

This is acceptable in a lab environment but **unsafe for production**.

---

## 7. Starting the Container

From the directory with `docker-compose.yml`, run:

```bash
docker compose up -d data-storage
```

---

## 8. Checking Status

To view logs:

```bash
docker compose logs -f data-storage
```

To check cluster health:

```bash
curl -s http://localhost:9200
curl -s http://localhost:9200/_cluster/health
```

Look for a `green` or `yellow` status in the response.

---
