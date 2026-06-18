# File Research: sources/virtualization/qemu/hw/virtio/virtio-nsm-pci.c

Provides the PCI wrapper for the AWS Nitro Secure Module virtio device.

Key entry points:
- `virtio_nsm_pci_realize()` forces virtio 1.0 and realizes the embedded `VirtIONSM` on the proxy bus.
- `virtio_nsm_pci_class_init()` installs the realize hook and marks the device as miscellaneous.
- `virtio_nsm_initfn()` initializes the embedded `TYPE_VIRTIO_NSM` device.
- `virtio_nsm_pci_register()` registers the PCI wrapper type.

Core mechanics:
- `VirtIONsmPCI` extends `VirtIOPCIProxy` and embeds `VirtIONSM vdev`.
- The registered base type is `virtio-nsm-pci-base`, with generic name `virtio-nsm-pci`.
- No additional PCI properties are defined in this file.

Important invariants:
- The wrapper always forces virtio 1.0 mode.
- Realize returns immediately if embedded device realization fails.

Filesystem/block relevance:
- No filesystem or block logic. It exposes a security/attestation device over virtio PCI.

Notable risks:
- The file is intentionally thin; device behavior and protocol validation live in `virtio-nsm.c`.
