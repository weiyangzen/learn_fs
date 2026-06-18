# sources/test-tools/kdevops/playbooks/update_etc_hosts.yml

Purpose: wrapper playbook that updates target `/etc/hosts` entries and disables cloud-init host management.

Important APIs/types/functions: targets `all:!localhost`, disables initial fact gathering, and invokes `update_etc_hosts`.

Control flow: role handles connectivity wait and fact gathering internally.

State/persistence behavior: delegated to role, mutating `/etc/hosts` and cloud-init config on targets.

Dependencies/integration: depends on inventory hostvars and network facts.

Risks/test signals: excludes localhost but affects every target. Test signals are resolvable hostnames and idempotent `/etc/hosts` changes.
