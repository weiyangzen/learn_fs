# File Research: sources/virtualization/qemu/hw/virtio/virtio-input-host-pci.c

Provides the PCI wrapper type for the host-backed virtio input device.

Key entry points:
- `virtio_host_initfn()` embeds and initializes a `VirtIOInputHost` virtio device inside the PCI proxy object using `virtio_instance_init_common()`.
- `virtio_input_host_pci_register()` registers the type through `virtio_pci_types_register()`.

Core mechanics:
- Defines `TYPE_VIRTIO_INPUT_HOST_PCI` as `virtio-input-host-pci`.
- `VirtIOInputHostPCI` extends `VirtIOPCIProxy` and contains a `VirtIOInputHost vdev`.
- The `VirtioPCIDeviceTypeInfo` parent is `TYPE_VIRTIO_INPUT_PCI`, so common virtio-input PCI behavior comes from `virtio-input-pci.c`.

Important invariants:
- The embedded virtio device type is `TYPE_VIRTIO_INPUT_HOST`.
- No class-specific PCI IDs or properties are added here; it inherits the input PCI base behavior.

Filesystem/block relevance:
- No filesystem or block path involvement. This is a small virtio PCI transport binding for input devices.

Notable risks:
- Misregistration would make `virtio-input-host-pci` unavailable or incorrectly inherit input PCI behavior, but the file has no runtime logic beyond type initialization.
