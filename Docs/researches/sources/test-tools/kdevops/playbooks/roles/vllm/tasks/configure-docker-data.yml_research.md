# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/configure-docker-data.yml

Purpose: configures Docker to use `/data/docker`, optionally adds a registry mirror, migrates existing Docker data, and prepares vLLM/minikube data directories.

Important APIs/types/functions: `file`, `stat`, `slurp`, `from_json`, `set_fact`, mirror auto-detection through `/mirror/docker/registry` and IP curl, `copy` to `/etc/docker/daemon.json`, `systemd`, shell `mv`, and directory creation.

Control flow: creates `/data/docker`, reads or initializes `daemon.json`, detects Docker mirror path or HTTP endpoint, merges `data-root` and optional `registry-mirrors`, writes daemon config, stops Docker if changed, moves existing `/var/lib/docker` content to `/data/docker`, removes empty old directory, restarts/enables Docker, and creates minikube/vLLM directories.

State/persistence behavior: mutates `/etc/docker/daemon.json`, Docker service state, Docker data root, `/var/lib/docker`, `/data/docker`, `/data/minikube`, and vLLM data directories.

Dependencies/integration: included for Docker and production-stack vLLM deployments. Depends on Docker service, mirror variables, and systemd.

Risks/test signals: Docker data migration can fail or leave split state if interrupted; JSON merge must preserve existing daemon options. Test signals are valid daemon JSON, Docker restart success, `docker info` data root, and created `/data` directories.
