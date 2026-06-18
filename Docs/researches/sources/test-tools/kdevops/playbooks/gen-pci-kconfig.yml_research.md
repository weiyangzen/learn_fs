# sources/test-tools/kdevops/playbooks/gen-pci-kconfig.yml

Purpose: Ansible entrypoint that generates dynamic PCIe passthrough Kconfig files for libvirt guests.

Important APIs/types/functions: targets `localhost` and invokes role `gen_pci_kconfig`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `gen_pci_kconfig`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is generated Kconfig fragments.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/gen_pci_kconfig` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
