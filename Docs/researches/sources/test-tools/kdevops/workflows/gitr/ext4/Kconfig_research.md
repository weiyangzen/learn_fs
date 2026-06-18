## sources/test-tools/kdevops/workflows/gitr/ext4/Kconfig

Purpose: Defines ext4 block device, filesystem label, and mount options for gitr.

Important APIs/types/functions: Symbols are `GITR_EXT4_DEVICE`, `GITR_EXT4_LABEL`, and `GITR_EXT4_MOUNT_OPTS`.

Control flow: Device defaults are selected by infrastructure backend and storage type. Label defaults to `gitr`; mount options default to `defaults`.

State and persistence: Stored in `.config`, then translated to Ansible args.

Dependencies and integration points: Active only when `GITR_EXT4` is selected. Relies on extra storage provisioning matching the default path.

Risks and test signals: Cloud/local device naming is the main risk. Test by validating the target device and rendered `gitr_fstype=ext4` args.
