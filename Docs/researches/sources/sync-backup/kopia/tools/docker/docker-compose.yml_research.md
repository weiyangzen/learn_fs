<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/docker-compose.yml -->
# sources/sync-backup/kopia/tools/docker/docker-compose.yml

This compose file defines a sample Kopia container deployment. The service uses `kopia/kopia:latest`, runs as root, restarts unless stopped, enables privileged/SYS_ADMIN/AppArmor-unconfined settings, maps devices and volumes for config/cache/logs/repository/data, and exposes the web/server port.

Control flow is declarative Docker Compose configuration. It is intended as an example operational deployment rather than test code.

State persists through mounted host volumes for configuration, cache, logs, repository, and backed-up data. Dependencies are Docker Compose, host mount paths, and Linux privilege support. Risks include broad container privileges, root user operation, accidental exposure of server port, and users needing to customize volumes before production use. Signals are manual compose runs and Docker image compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/docker-compose.yml -->
