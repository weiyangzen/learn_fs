# sources/test-tools/kdevops/playbooks/postfix_relay_host.yml

Purpose: Ansible entrypoint that configures Postfix with a custom relay host.

Important APIs/types/functions: targets `localhost` and invokes role `postfix_relay_host`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `postfix_relay_host`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is Postfix relay configuration.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/postfix_relay_host` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
