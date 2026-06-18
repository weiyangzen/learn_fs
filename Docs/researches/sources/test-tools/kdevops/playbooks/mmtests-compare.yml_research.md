# sources/test-tools/kdevops/playbooks/mmtests-compare.yml

Purpose: Ansible entrypoint that compares mmtests results when baseline/dev mode is enabled.

Important APIs/types/functions: targets `localhost` and invokes role `mmtests_compare`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `mmtests_compare`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is local comparison artifacts.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/mmtests_compare` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
