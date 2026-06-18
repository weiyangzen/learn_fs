<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml

Source read: complete file, 14 lines, 449 bytes, sha256 `65b2f8190dace395`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml_research.md`.

Purpose: defaults for generic block device filesystem creation and mounting.

Important APIs/types/functions: `disk_setup_device`, `disk_setup_fstype`, `disk_setup_mount_opts`, `disk_setup_label`, `disk_setup_fs_opts`, `disk_setup_path`, `disk_setup_user`, `disk_setup_group`, `disk_setup_mode`, and `disk_setup_env`.

Control flow: no tasks; consumed by `create_partition/tasks/main.yml`.

State and persistence behavior: defaults describe an XFS filesystem labeled `data` mounted at `/data` with broad sticky permissions.

Dependencies and integration: used by `create_data_partition` and any role needing generic disk formatting/mounting.

Risks: placeholder `disk_setup_device` must be overridden. The default mode `u=rwx,g=rwx,o=rwxt` is permissive and appropriate only for shared data semantics.

Test signals: variable validation should ensure `disk_setup_device` is not left as `/dev/some-block-device` before destructive filesystem tasks run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/defaults/main.yml -->
