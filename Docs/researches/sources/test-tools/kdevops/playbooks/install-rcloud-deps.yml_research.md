# sources/test-tools/kdevops/playbooks/install-rcloud-deps.yml

Purpose: Ansible entrypoint that installs rcloud build dependencies.

Important APIs/types/functions: targets `localhost` and invokes role `install-rcloud-deps`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `install-rcloud-deps`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is controller packages.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/install-rcloud-deps` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
