## sources/test-tools/kdevops/workflows/gitr/btrfs/Kconfig

Purpose: Supplies btrfs device, label, and mount-option settings for running Git regression tests on btrfs.

Important APIs/types/functions: Symbols are `GITR_BTRFS_DEVICE`, `GITR_BTRFS_LABEL`, and `GITR_BTRFS_MOUNT_OPTS`.

Control flow: Device defaults vary by backend and storage driver: libvirt NVMe/virtio/IDE, AWS m5ad, GCE, and Azure get different device paths. Label and mount options have simple defaults.

State and persistence: Values persist in `.config` and become gitr Ansible vars.

Dependencies and integration points: Used when `GITR_BTRFS` is selected. Integrates with kdevops storage provisioning and the btrfs gitr Makefile.

Risks and test signals: Device path defaults can drift with provider images. Verify the configured device exists before mkfs/mount and inspect `gitr_device` in extra vars.
