<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml

Source read: complete file, 159 lines, 4705 bytes, sha256 `222082ba7a4e87ec`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml_research.md`.

Purpose: generic filesystem creation, mount, and permission setup for a configured block device/path.

Important APIs/types/functions: optional `include_vars`, `import_tasks: install-deps/main.yml`, `mountpoint -q`, `/etc/fstab` awk/grep shell checks, `lsblk` label and partition inspection, `ansible.builtin.stat`, `community.general.filesystem`, `ansible.posix.mount`, and `ansible.builtin.file`.

Control flow: load vars; install mkfs deps; check whether target path is mounted, present in fstab, and whether any block label matches; stat the device if not already configured; wipe old filesystem if not in fstab/mounted/labeled; inspect partitions; set `part_mounts`; create filesystem when device has no partitions and no matching label/mount; mount by `LABEL="{{ disk_setup_label }}"`; ensure directory permissions.

State and persistence behavior: potentially destructive filesystem wipe/create on `disk_setup_device`, persistent fstab/mount state via `ansible.posix.mount`, and ownership/mode changes on `disk_setup_path`.

Dependencies and integration: used by data partition role and any workflow needing local block storage. Depends on mkfs tools, lsblk output shape, labels, and caller-provided device/path/user/group/fstype.

Risks: destructive operations rely on shell-derived mount/fstab/label checks. `part_mounts_item` is referenced but not looped or defined in this file, making create/mount conditions hard to reason about and possibly broken. Matching any label globally can skip formatting even if the label is on the wrong device.

Test signals: run in a disposable VM for cases: fresh whole disk, already mounted path, fstab entry present, existing label, device absent, and device with partitions. Confirm idempotent second run and correct fstab entry.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/main.yml -->
