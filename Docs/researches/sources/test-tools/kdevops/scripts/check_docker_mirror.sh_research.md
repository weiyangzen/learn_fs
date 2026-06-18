# sources/test-tools/kdevops/scripts/check_docker_mirror.sh

Purpose: Kconfig helper that detects Docker mirror directory, registry container, and registry endpoint status.

Important APIs/types/functions: env defaults `DOCKER_MIRROR_PATH` and `DOCKER_REGISTRY_PORT`, functions `check_registry_running` and `check_registry_accessible`, `docker ps`, `curl`, and case handling for Kconfig symbols/status.

Control flow: if mirror directory exists, answers `y` for enable checks, checks registry directory plus HTTP accessibility for use, suggests install when registry is absent or stopped, reports registry running, or prints human-readable status. Defaults to `n`.

State/persistence behavior: read-only filesystem/Docker/HTTP inspection.

Dependencies/integration: used by Kconfig defaults and vLLM Docker mirror configuration.

Risks/test signals: assumes local registry name `kdevops-docker-mirror`; HTTP check only probes localhost. Test signals are `y/n` for Kconfig modes and status text for user mode.
