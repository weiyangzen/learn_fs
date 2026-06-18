# File Research: sources/virtualization/qemu/hw/virtio/virtio-md-pci.c

Defines the abstract PCI base class for virtio-based memory devices and centralizes memory-device hotplug/unplug coordination.

Key entry points:
- `virtio_md_pci_pre_plug()` validates the generic `MemoryDeviceState` and then calls the bus hotplug handler's pre-plug hook when present.
- `virtio_md_pci_plug()` plugs the memory device first, then calls the bus hotplug handler and rolls memory-device state back if bus plug fails.
- `virtio_md_pci_unplug_request()` validates class support, bus support, and device-specific unplug preconditions, then forwards an async unplug request or performs synchronous unplug/unparent.
- `virtio_md_pci_unplug()` unplugs the memory device while still realized, then calls bus unplug handling, with best-effort recovery on failure.
- Type registration creates abstract `TYPE_VIRTIO_MD_PCI` as a `TYPE_VIRTIO_PCI` subclass implementing `TYPE_MEMORY_DEVICE`.

Core mechanics:
- `VirtIOMDPCIClass` can provide `unplug_request_check`; devices lacking it are considered non-unpluggable.
- The code distinguishes bus hotplug handlers from device hotplug state to enforce plug/unplug ordering.
- Memory-device state changes are coordinated with machine-level `memory_device_*()` helpers and bus-level `hotplug_handler_*()` hooks.

Important invariants:
- Hotplugged virtio memory devices require a bus hotplug handler.
- Plug order is memory-device first, bus handler second; unplug order is memory-device first while the device is still realized, then bus handler.
- If bus plug fails, the memory-device plug is undone.
- If bus unplug unexpectedly fails, the code tries to re-plug memory-device state.

Filesystem/block relevance:
- No direct filesystem or block behavior. It supports memory hotplug infrastructure used by virtio memory devices.

Notable risks:
- Unplug failure recovery is best effort and comments mark it as unexpected.
- Without a bus hotplug handler, hotunplug is rejected and unexpected direct unplug falls back to warning plus `qdev_unrealize()`.
