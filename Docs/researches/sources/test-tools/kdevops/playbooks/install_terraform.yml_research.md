# sources/test-tools/kdevops/playbooks/install_terraform.yml

Purpose: Ansible entrypoint that installs Terraform on the controller.

Important APIs/types/functions: targets `localhost` and invokes role `install_terraform`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `install_terraform`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is Terraform binary/package state.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/install_terraform` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
