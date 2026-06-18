# sources/test-tools/kdevops/playbooks/krb5.yml

Purpose: Ansible entrypoint that sets up Kerberos and configures NFS clients for authentication.

Important APIs/types/functions: targets `krb5` and invokes role `krb5`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `krb5`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is Kerberos client/server config.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/krb5` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
