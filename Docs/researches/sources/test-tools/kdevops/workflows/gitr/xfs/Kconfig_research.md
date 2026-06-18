## sources/test-tools/kdevops/workflows/gitr/xfs/Kconfig

Purpose: Defines XFS device, label, and mount options for gitr.

Important APIs/types/functions: Symbols are `GITR_XFS_DEVICE`, `GITR_XFS_LABEL`, and `GITR_XFS_MOUNT_OPTS`.

Control flow: Device defaults branch on libvirt storage driver and cloud backend. Label and mount options are simple strings.

State and persistence: Values persist in `.config` and are translated into gitr vars.

Dependencies and integration points: Active when `GITR_XFS` is selected. Depends on provisioned extra storage matching the selected path.

Risks and test signals: Wrong device path can be destructive. Validate inventory storage and generated `gitr_device` before running setup.
