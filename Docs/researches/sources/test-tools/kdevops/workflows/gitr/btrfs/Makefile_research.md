## sources/test-tools/kdevops/workflows/gitr/btrfs/Makefile

Purpose: Emits gitr btrfs filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=btrfs`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and appends `btrfs` to `GITR_ENABLED_TEST_GROUPS`.

Control flow: Straight-line Make variable appends from Kconfig.

State and persistence: No direct state; it derives from `.config`.

Dependencies and integration points: Included by gitr Makefile when btrfs is selected. Consumed by the gitr Ansible playbook for formatting and mounting.

Risks and test signals: Ensure quoting preserves mount options. Validate `extra_vars.yaml` and target mount output.
