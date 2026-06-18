# sources/test-tools/kdevops/playbooks/pkg.yml

Purpose: Ansible entrypoint that wraps package-name handling for target hosts.

Important APIs/types/functions: targets `baseline:dev` and invokes role `pkg`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `pkg`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is package mapping/install state.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/pkg` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
