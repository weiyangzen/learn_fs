## sources/test-tools/kdevops/workflows/gitr/tmpfs/Kconfig

Purpose: Defines tmpfs mount options for gitr.

Important APIs/types/functions: Single public symbol `GITR_TMPFS_MOUNT_OPTS`, defaulting to `size=75%`.

Control flow: No branching; the configured string controls tmpfs mount behavior.

State and persistence: Stored in `.config` and emitted to gitr Ansible vars.

Dependencies and integration points: Used when `GITR_TMPFS` is selected and mapped by the tmpfs gitr Makefile.

Risks and test signals: Large Git test runs may exceed the tmpfs size. Test by checking target memory/swap and available space after mount.
