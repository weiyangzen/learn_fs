<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml

Source read: complete file, 4 lines, 117 bytes, sha256 `e907ecb34ffa53a1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml_research.md`.

Purpose: defaults for creating the primary kdevops data partition.

Important APIs/types/functions: `kdevops_enable_terraform` and `kdevops_use_declared_hosts`.

Control flow: no tasks; variables are used by `create_data_partition/tasks/main.yml` to decide whether AWS terraform block-device discovery is needed.

State and persistence behavior: no direct mutation.

Dependencies and integration: feeds the wrapper role that calls `create_partition` with data device/filesystem/path/user/group variables.

Risks: defaults avoid terraform-specific mapping; provider runs must set required variables elsewhere.

Test signals: with terraform disabled, the role should proceed directly to `create_partition` using `data_device` values from inventory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_data_partition/defaults/main.yml -->
