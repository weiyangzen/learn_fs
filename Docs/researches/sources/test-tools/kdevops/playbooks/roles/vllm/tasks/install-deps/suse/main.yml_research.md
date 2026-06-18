# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/suse/main.yml

Purpose: installs SUSE-family dependencies for vLLM.

Important APIs/types/functions: zypper/package installs for Docker/system tools, Python development, benchmark packages, and Kubernetes Python client.

Control flow: sequential package groups are installed without further branching.

State/persistence behavior: changes package state.

Dependencies/integration: selected by vLLM install dispatcher for SUSE OS family.

Risks/test signals: package naming/repo availability is the key SUSE risk. Test signals are successful package installation and later Docker/Python/Kubernetes operations.
