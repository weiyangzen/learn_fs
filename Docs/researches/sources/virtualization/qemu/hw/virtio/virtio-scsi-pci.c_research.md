# File Research: sources/virtualization/qemu/hw/virtio/virtio-scsi-pci.c

## Purpose
PCI wrapper for the virtio SCSI controller device.

## Main Responsibilities
- Defines `VirtIOSCSIPCI`, embedding `VirtIOPCIProxy` and `VirtIOSCSI`.
- Provides PCI wrapper properties:
  - `ioeventfd`, default enabled.
  - `vectors`, default unspecified.
- `virtio_scsi_pci_realize()` auto-selects `num_queues` via `virtio_pci_optimal_num_queues()` when configured for automatic queue count.
- Defaults MSI-X vector count to `num_queues + VIRTIO_SCSI_VQ_NUM_FIXED + 1` when unspecified.
- Preserves command-line compatibility by setting the child bus name to `<proxy-id>.0` when the PCI proxy has an ID.
- Realizes the embedded `VirtIOSCSI` on the virtio-pci bus.
- Class initialization sets storage category, PCI vendor/device/class IDs, revision, transport realization callback, and properties.
- Registers generic, transitional, and non-transitional type names.

## Integration Points
- Uses `VirtIOSCSIConf` for queue configuration.
- Uses generic virtio-pci queue-count helper to balance vCPU count, MSI-X vector limits, and `VIRTIO_QUEUE_MAX`.
- Exposes PCI class `PCI_CLASS_STORAGE_SCSI`, making this a storage controller from the guest PCI perspective.

## Filesystem/Storage Relevance
This is the PCI transport binding for virtio-scsi, a major guest storage path. It determines queue scaling and MSI-X vector allocation, which directly affect SCSI I/O parallelism and interrupt behavior.
