<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml

Source read: complete file, 56 lines, 1467 bytes, sha256 `a5c8890df87312b9`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml_research.md`.

Purpose: mount a tmpfs at the configured path and set its permissions.

Important APIs/types/functions: optional `include_vars`, `command mountpoint -q`, shell `/etc/fstab` check, `ansible.posix.mount`, and `ansible.builtin.file`.

Control flow: load extra vars; inspect current mountpoint; inspect fstab; mount tmpfs with throttle 1 when not mounted; then set owner/group/mode on the mounted path.

State and persistence behavior: creates a persistent mount entry through `ansible.posix.mount` and changes directory metadata. Data stored on tmpfs is non-persistent across reboot.

Dependencies and integration: alternative storage setup for workflows that do not need durable `/data`.

Risks: mount condition uses `when: mountpoint_stat != 0` rather than `mountpoint_stat.rc != 0`, likely making idempotence unreliable. The fstab check result is registered but not used.

Test signals: first run should mount tmpfs; second run should be idempotent. Validate the condition against the registered rc field.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_tmpfs/tasks/main.yml -->
