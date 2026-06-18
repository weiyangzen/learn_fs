# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-helm.yml

Purpose: installs Helm if missing and verifies it.

Important APIs/types/functions: `stat`, `get_url` for installer script, command execution of installer, `helm version`, and debug output.

Control flow: checks for `/usr/local/bin/helm`, downloads and runs installer only when absent, verifies version, and displays it.

State/persistence behavior: writes Helm binary and temporary installer script.

Dependencies/integration: included by production-stack deployment; depends on network access to Helm installer and root privileges to install.

Risks/test signals: remote installer execution and version drift are risks. Test signals are `helm version` success.
