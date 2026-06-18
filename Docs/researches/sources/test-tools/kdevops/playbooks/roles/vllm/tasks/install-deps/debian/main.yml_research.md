# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/debian/main.yml

Purpose: installs Debian-family dependencies for vLLM Docker/Kubernetes benchmarking.

Important APIs/types/functions: `apt` update, `dpkg-query` for docker-ce detection, package installs with or without `docker.io`, Python development/benchmark/Kubernetes packages, and user group modification.

Control flow: refreshes apt, checks whether Docker CE is already installed, installs system dependencies with Docker only if needed, installs Python build and benchmarking packages, installs Python Kubernetes client, and adds current user to Docker group.

State/persistence behavior: changes apt package state and user group membership.

Dependencies/integration: selected by vLLM install dispatcher for Debian OS family.

Risks/test signals: mixing Docker CE and distro Docker packages can conflict; group membership needs reconnect. Test signals are package install success, Docker command availability, and Python imports.
