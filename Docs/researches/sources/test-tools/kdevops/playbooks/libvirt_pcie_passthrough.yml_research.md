# sources/test-tools/kdevops/playbooks/libvirt_pcie_passthrough.yml

Purpose: Ansible entrypoint that configures PCIe passthrough for libvirt VMs.

Important APIs/types/functions: targets `localhost` and invokes role `libvirt_pcie_passthrough`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `libvirt_pcie_passthrough`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is libvirt XML/device binding state.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/libvirt_pcie_passthrough` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
