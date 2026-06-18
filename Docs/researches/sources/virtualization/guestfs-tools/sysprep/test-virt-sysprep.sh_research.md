# File Research: sources/virtualization/guestfs-tools/sysprep/test-virt-sysprep.sh

General no-modification smoke test for `virt-sysprep`.

Key behavior:
- Gets enabled-by-default operations from `virt-sysprep --list-operations`, selecting starred rows and joining operation names with commas.
- Runs `virt-sysprep -q -n --enable "$operations"` against phony Debian, Fedora, Ubuntu, and Windows images when present and non-empty.
- Uses `-n`, so guests are not modified.
- Mentions MD RAID Fedora images as intentionally skipped because mdadm is problematic for many users.

Research notes:
- This verifies default operations can inspect/process representative test guests without writing changes.
