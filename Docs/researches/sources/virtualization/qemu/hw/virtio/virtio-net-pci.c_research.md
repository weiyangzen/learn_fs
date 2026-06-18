# File Research: sources/virtualization/qemu/hw/virtio/virtio-net-pci.c

Provides the PCI wrapper for virtio-net.

Key entry points:
- `virtio_net_pci_realize()` chooses a default vector count from queue count, config interrupt, and control virtqueue, sets the netclient name, and realizes the embedded `VirtIONet`.
- `virtio_net_pci_class_init()` configures PCI ROM/vendor/device/revision/class metadata, SR-IOV VF user-creatable support, category, properties, and realize hook.
- `virtio_net_pci_instance_init()` initializes the embedded virtio-net device and aliases the wrapper `bootindex` property to the embedded device.
- `virtio_net_pci_register()` registers base, transitional, and non-transitional virtio-net PCI types.

Core mechanics:
- `VirtIONetPCI` extends `VirtIOPCIProxy` and embeds `VirtIONet vdev`.
- Default `vectors` is unspecified until realize; realize computes `2 * max(queue_pairs, 1) + 1 config + 1 control`.
- The PCI ROM is `efi-virtio.rom`; vendor/device are Red Hat/Qumranet virtio-net identifiers.
- Properties include `ioeventfd` and `vectors`.

Important invariants:
- Netclient naming uses the PCI wrapper device id and QOM type name.
- Transitional and non-transitional variants are registered by `virtio_pci_types_register()`.
- `bootindex` is owned by the embedded net device but exposed on the PCI wrapper.

Filesystem/block relevance:
- No filesystem or block logic. It is a network virtio PCI wrapper and a reference pattern for virtio PCI binding.

Notable risks:
- Incorrect vector calculation would affect multiqueue interrupt layout.
- Guest driver matching depends on PCI class/vendor/device and transitional type registration.
