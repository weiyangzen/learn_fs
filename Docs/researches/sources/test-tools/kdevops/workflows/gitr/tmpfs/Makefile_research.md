## sources/test-tools/kdevops/workflows/gitr/tmpfs/Makefile

Purpose: Emits gitr variables for tmpfs-backed testing.

Important APIs/types/functions: Adds `gitr_fstype=tmpfs`, `gitr_uses_no_devices='True'`, `gitr_mount_opts`, and enabled group `tmpfs`.

Control flow: Straight-line mapping from `CONFIG_GITR_TMPFS_MOUNT_OPTS`.

State and persistence: No direct persistence; feeds Ansible vars.

Dependencies and integration points: Included by the main gitr Makefile when tmpfs is selected.

Risks and test signals: Mount option string must be valid for target kernels. Verify by running only setup/mount tags before full Git regression.
