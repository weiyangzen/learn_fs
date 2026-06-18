# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/redhat/main.yml

Purpose: installs Red Hat-family vLLM dependencies with yum/dnf split for old vs newer releases.

Important APIs/types/functions: `yum`/`dnf` package installs for Docker/system tools, Python development packages, benchmarking libraries, and Python Kubernetes client.

Control flow: branches on `ansible_distribution_major_version <= 7` for yum package sets and `>= 8` for dnf package sets across system, development, benchmarking, and Kubernetes client packages.

State/persistence behavior: changes system package state.

Dependencies/integration: selected by vLLM install dispatcher for RedHat OS family.

Risks/test signals: package names differ across RHEL clones and EPEL availability. Test signals are package install success, Docker availability, Python venv/pip and Kubernetes client imports.
