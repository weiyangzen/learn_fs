# File Research: sources/virtualization/qemu/hw/virtio/virtio-mem-pci.c

Implements the PCI wrapper and `MemoryDeviceClass` integration for the virtio-mem device.

Key entry points:
- `virtio_mem_pci_realize()` defaults `nvectors` to 2 when unspecified, forces virtio 1.0, and realizes the embedded `VirtIOMEM`.
- `virtio_mem_pci_get_addr()` / `virtio_mem_pci_set_addr()` proxy the memory-device address property to the embedded virtio-mem object.
- `virtio_mem_pci_get_memory_region()`, `virtio_mem_pci_decide_memslots()`, and `virtio_mem_pci_get_memslots()` delegate memory-region and memslot decisions to the embedded virtio-mem class.
- `virtio_mem_pci_fill_device_info()` allocates and fills QAPI `VirtioMEMDeviceInfo`, including the PCI device id when present.
- `virtio_mem_pci_size_change_notify()` emits `MEMORY_DEVICE_SIZE_CHANGE` QAPI events when the embedded plugged size changes.
- `virtio_mem_pci_unplug_request_check()` delegates unplug precondition checks to the embedded virtio-mem class.
- `virtio_mem_pci_get_requested_size()` / `virtio_mem_pci_set_requested_size()` expose requested-size as a wrapper property, blocking changes once pending unplug deletion is in progress.

Core mechanics:
- `VirtIOMEMPCI` extends the abstract `VirtIOMDPCI` base and embeds `VirtIOMEM vdev`.
- The wrapper implements the `MemoryDeviceClass` methods expected by machine hotplug code.
- Class properties include `ioeventfd` and `vectors`, with `vectors` defaulting to `DEV_NVECTORS_UNSPECIFIED`.
- Instance init registers a size-change notifier with the embedded virtio-mem device and adds wrapper aliases for block-size and current-size properties.

Important invariants:
- The PCI wrapper is registered with base type `virtio-mem-pci-base` and generic name `virtio-mem-pci`.
- The requested-size property cannot be changed after unplug request processing has marked the device pending deletion.
- The notifier is not removed explicitly because the wrapper and embedded virtio device are expected to disappear together.
- PCI class/revision are set to miscellaneous virtio PCI values.

Filesystem/block relevance:
- No direct filesystem or block logic. Virtio-mem affects guest physical memory availability, which can indirectly affect page cache and filesystem workloads.

Notable risks:
- The wrapper relies on the embedded virtio-mem class for most validation; wrapper property aliasing must remain consistent with core property names.
- Blocking requested-size changes during pending unplug avoids memory being re-hotplugged before device deletion completes.
