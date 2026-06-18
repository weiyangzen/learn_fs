## sources/test-tools/kdevops/workflows/gitr/ext4/Makefile

Purpose: Emits gitr ext4 filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=ext4`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and enabled group `ext4`.

Control flow: Straight-line mapping from `CONFIG_GITR_EXT4_*` symbols to `GITR_ARGS`.

State and persistence: No direct writes; used to produce Ansible invocation variables.

Dependencies and integration points: Included from the main gitr Makefile when ext4 is selected.

Risks and test signals: Wrong device selection can destroy data on a target. Test only on provisioned disposable disks and verify generated variables before running.
