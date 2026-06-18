# sources/test-tools/kdevops/playbooks/base_image.yml

Purpose: Ansible entrypoint that creates a libvirt base OS image on the controller.

Important APIs/types/functions: targets `localhost` and invokes role `base_image`. The file is intentionally thin; the role is the primary implementation API and this playbook provides the stable command target for make/automation.

Control flow: Ansible selects the target host group, loads inventory and generated variables, then transfers execution to role `base_image`.

State/persistence behavior: direct state mutation is delegated to the role; expected persistent surface is local image artifacts under the configured image storage.

Dependencies/integration: integrates Kconfig-generated variables, inventory groups, and the role under `playbooks/roles/base_image` with higher-level kdevops make targets.

Risks/test signals: wrapper-level risk is mainly host-group or role-name drift. Test signals are Ansible syntax success, role discovery, idempotent reruns, and expected role artifacts being present after execution.
