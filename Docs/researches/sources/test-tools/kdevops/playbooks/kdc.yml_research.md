# sources/test-tools/kdevops/playbooks/kdc.yml

Purpose: Ansible entrypoint that sets up an MIT Kerberos V5 KDC.

Important APIs/types/functions: targets `kdc` and invokes role `kdc`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `kdc`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is realm, principals, and KDC service config.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/kdc` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
