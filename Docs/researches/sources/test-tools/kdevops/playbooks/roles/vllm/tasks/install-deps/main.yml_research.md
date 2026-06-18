# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/install-deps/main.yml

Purpose: vLLM OS-specific dependency dispatcher.

Important APIs/types/functions: includes role `pkg`, then includes Debian, SUSE, or RedHat task files based on `ansible_facts.os_family`.

Control flow: generic package setup first, then distro branch.

State/persistence behavior: delegated to package tasks.

Dependencies/integration: used early in vLLM role main flow.

Risks/test signals: unsupported OS family means no dependencies installed. Test signals are selected include and later deployment prerequisites.
