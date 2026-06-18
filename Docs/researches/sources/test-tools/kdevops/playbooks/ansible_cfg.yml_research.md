# sources/test-tools/kdevops/playbooks/ansible_cfg.yml

Purpose: Ansible entrypoint that generates or updates the Ansible configuration used by kdevops runs.

Important APIs/types/functions: targets `localhost` and invokes role `ansible_cfg`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `ansible_cfg`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is local Ansible config files and interpreter settings.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/ansible_cfg` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
