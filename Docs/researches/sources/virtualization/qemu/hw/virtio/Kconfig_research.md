# File Research: sources/virtualization/qemu/hw/virtio/Kconfig

Kconfig declarations for QEMU virtio and vhost-user/vhost-vdpa device families.

Key contents:
- Base `VIRTIO` symbol selected by virtio transports.
- Transport symbols: `VIRTIO_PCI`, `VIRTIO_MMIO`, `VIRTIO_CCW`.
- Core virtio devices: RNG, NSM, IOMMU, balloon, crypto.
- Memory-device support gates: `VIRTIO_MD_SUPPORTED`, `VIRTIO_MD`, `VIRTIO_PMEM_SUPPORTED`, `VIRTIO_PMEM`, `VIRTIO_MEM_SUPPORTED`, `VIRTIO_MEM`.
- vhost/vhost-user devices: vsock, i2c, rng, fs, gpio, vdpa dev, sound, SCMI, SPI, test, RTC.

Dependency model:
- Transports select `VIRTIO`; PCI and CCW also select `VIRTIO_MD_SUPPORTED`.
- Virtio memory devices require a supported transport/board path and select `MEM_DEVICE` through `VIRTIO_MD`.
- `VIRTIO_NSM` requires `LIBCBOR && VIRTIO`.
- `VIRTIO_IOMMU` requires `PCI && VIRTIO`.
- vhost-user devices generally require `VIRTIO && VHOST_USER`; vhost-vdpa requires `VIRTIO && VHOST_VDPA && LINUX`.

Notable role:
- This file is build-configuration glue rather than runtime code. It controls which virtio device implementations are available for a target based on platform, transport, and dependency symbols.
