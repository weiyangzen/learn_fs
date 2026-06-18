# sources/test-tools/kdevops/playbooks/common.yml

Purpose: Ansible entrypoint that runs common host preparation shared by workflows.

Important APIs/types/functions: targets `baseline:dev` and invokes role `common`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `common`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is packages, directories, users, and common host config.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/common` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
