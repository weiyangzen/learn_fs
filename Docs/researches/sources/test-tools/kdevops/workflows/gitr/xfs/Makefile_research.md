## sources/test-tools/kdevops/workflows/gitr/xfs/Makefile

Purpose: Emits gitr XFS filesystem variables.

Important APIs/types/functions: Adds `gitr_fstype=xfs`, `gitr_uses_no_devices='False'`, `gitr_device`, `gitr_label`, `gitr_mount_opts`, and enabled group `xfs`.

Control flow: Straight-line Make argument emission.

State and persistence: No direct persistence.

Dependencies and integration points: Included by main gitr Makefile when XFS is selected and consumed by the gitr playbook.

Risks and test signals: Mount-option quoting and device correctness are the key checks. Inspect generated vars and target `findmnt`.
