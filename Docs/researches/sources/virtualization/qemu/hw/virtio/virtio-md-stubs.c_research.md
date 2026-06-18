# File Research: sources/virtualization/qemu/hw/virtio/virtio-md-stubs.c

Provides stub implementations for virtio memory-device PCI hotplug helpers when virtio-based memory devices are not supported in the build.

Key entry points:
- `virtio_md_pci_pre_plug()`
- `virtio_md_pci_plug()`
- `virtio_md_pci_unplug_request()`
- `virtio_md_pci_unplug()`

Core mechanics:
- Every function simply sets an error: `virtio based memory devices not supported`.
- Signatures match the real implementations in `virtio-md-pci.c`, allowing callers to link even when support is disabled.

Important invariants:
- These stubs do not mutate memory-device, bus, or hotplug state.
- Callers must treat the returned error as a hard unsupported-device condition.

Filesystem/block relevance:
- No filesystem or block behavior.

Notable risks:
- Build configurations using this file cannot hotplug or manage virtio-based memory devices; all such operations fail uniformly.
