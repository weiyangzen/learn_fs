# File Research: sources/virtualization/qemu/hw/virtio/virtio-iommu-pci.c

Provides the PCI wrapper for the virtio IOMMU device and enforces machine/PCI topology constraints before realizing the embedded IOMMU.

Key entry points:
- `virtio_iommu_pci_realize()` validates hotplug-handler support, validates configured reserved-region types, requires root-bus placement, links the embedded device to the primary PCI bus, forces virtio 1.0, and realizes the virtio IOMMU.
- `virtio_iommu_pci_class_init()` installs properties, marks the device non-hotpluggable, sets category/revision/class, and wires the realize hook.
- `virtio_iommu_pci_instance_init()` initializes the embedded `VirtIOIOMMU`.
- `virtio_iommu_pci_register()` registers the PCI wrapper type.

Core mechanics:
- `VirtIOIOMMUPCI` extends `VirtIOPCIProxy` and embeds `VirtIOIOMMU vdev`.
- Properties include `class` mapped to `VirtIOPCIProxy.class_code` and an array property `reserved-regions` stored in the embedded IOMMU.
- The wrapper sets the embedded IOMMU's `primary-bus` link to the PCI bus it is plugged into.

Important invariants:
- `virtio-iommu-pci` must be on a root PCI bus.
- Reserved-region property types must be `VIRTIO_IOMMU_RESV_MEM_T_RESERVED` or `VIRTIO_IOMMU_RESV_MEM_T_MSI`.
- The machine must provide a hotplug handler so IOMMU interactions with PCI hotplug can be coordinated.
- The PCI wrapper itself is not hotpluggable.

Filesystem/block relevance:
- Indirectly relevant to virtualized storage because assigned and emulated PCI devices can route DMA through this IOMMU. It does not implement block I/O itself.

Notable risks:
- Incorrect placement or missing machine hotplug support is rejected at realize time.
- Reserved-region validation is done before the embedded device is realized, preventing unsupported region types from reaching the IOMMU core.
