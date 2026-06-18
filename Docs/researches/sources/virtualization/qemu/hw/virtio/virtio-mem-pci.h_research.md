# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.h

Declares the PCI wrapper state for virtio-mem.

Key contents:
- Defines `TYPE_VIRTIO_MEM_PCI` as `virtio-mem-pci-base`.
- Declares the `VirtIOMEMPCI` instance checker.
- Defines `struct VirtIOMEMPCI` with:
  - `VirtIOMDPCI parent_obj`
  - embedded `VirtIOMEM vdev`
  - `Notifier size_change_notifier`

Core mechanics:
- The header connects the generic virtio memory-device PCI base (`virtio-md-pci.h`) with the concrete virtio-mem device (`virtio-mem.h`).
- It is included by `virtio-mem-pci.c` to implement the wrapper methods.

Important invariants:
- `VirtIOMEMPCI` is a `VirtIOMDPCI` subclass, so it participates in the memory-device hotplug flow defined by the abstract base.
- The embedded virtio-mem object and notifier are owned by the PCI wrapper instance.

Filesystem/block relevance:
- No filesystem or block behavior.

Notable risks:
- Structure layout must match QOM type registration in `virtio-mem-pci.c`.
