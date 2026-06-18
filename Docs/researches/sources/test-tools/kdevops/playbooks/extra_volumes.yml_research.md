# sources/test-tools/kdevops/playbooks/extra_volumes.yml

Purpose: Ansible entrypoint that sets up udev rules for `/dev/disk/kdevops/` extra volumes.

Important APIs/types/functions: targets `baseline:dev:service` and invokes role `extra_volumes`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `extra_volumes`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is udev rules and device symlinks.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/extra_volumes` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
