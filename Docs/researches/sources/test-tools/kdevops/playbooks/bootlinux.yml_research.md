# sources/test-tools/kdevops/playbooks/bootlinux.yml

Purpose: Ansible entrypoint that gets, builds, installs, or boots Linux according to bootlinux variables.

Important APIs/types/functions: targets `all` and invokes role `bootlinux`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `bootlinux`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is kernel source/build/install state on targets.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/bootlinux` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
