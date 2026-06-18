<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/docker-mirror-setup.sh -->
# sources/test-tools/kdevops/scripts/docker-mirror-setup.sh

Purpose: sets up a local Docker registry mirror for kdevops workflows. It creates mirror directories, writes a registry proxy configuration for Docker Hub, runs a `registry:2` container, and can emit daemon mirror configuration.

Important APIs and functions: `check_docker()` validates docker CLI and daemon access; `setup_directories()` creates `$MIRROR_DIR/{registry,images,config}` with sudo; `create_registry_config()` writes registry YAML through `/tmp`; `start_registry()` replaces any existing named container and runs the mirror; `configure_docker_daemon()` writes or stages `/etc/docker/daemon.json`; `main()` orchestrates setup.

Control flow: if the first arg is `--configure-daemon`, only daemon configuration runs. Otherwise the script checks Docker, creates directories/config, starts the registry, verifies `http://localhost:$REGISTRY_PORT/v2/`, and prints next steps.

State and persistence: writes under the mirror directory, creates/removes Docker containers, writes temp config files, may modify `/etc/docker/daemon.json`, and restarts Docker when no existing daemon config exists.

Dependencies and integration: Docker, sudo, curl, systemctl. Related Makefile and Ansible role targets provide a richer docker-mirror workflow.

Risks: existing daemon config is not merged automatically, only backed up/staged. Container replacement is destructive for the named container but preserves mounted registry data. Registry uses insecure localhost HTTP. Test signals include shellcheck, dry-run/container integration tests in a disposable Docker host, and daemon-config tests with existing and absent config.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/docker-mirror-setup.sh -->
