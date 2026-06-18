# File Research: sources/virtualization/qemu/hw/virtio/vhost-vdpa.c

## Purpose
Implements the vhost-vDPA backend `VhostOps` for QEMU virtio devices, bridging generic vhost lifecycle calls to Linux vhost-vDPA ioctls and IOTLB messages. It owns vDPA-specific memory listener behavior, device status sequencing, host notifier mmap setup, and shadow virtqueue setup used for migration/logging paths.

## Key Elements
- DMA map/unmap path: `vhost_vdpa_dma_map()` and `vhost_vdpa_dma_unmap()` emit `VHOST_IOTLB_MSG_V2` update/invalidate messages to the vDPA device fd, including ASID support when available.
- Memory listener: `vhost_vdpa_listener_region_add()`, `vhost_vdpa_listener_region_del()`, and `vhost_vdpa_listener_commit()` translate QEMU RAM/IOMMU region changes into vDPA IOTLB updates, including batched begin/end messages when `VHOST_BACKEND_F_IOTLB_BATCH` is negotiated.
- IOMMU handling: `vhost_vdpa_iommu_region_add()` registers notifiers and replays mappings; `vhost_vdpa_iommu_map_notify()` maps or unmaps translated IOTLB entries against the vDPA device.
- Backend setup: `vhost_vdpa_init()` negotiates backend capabilities, initializes shadow virtqueues, blocks migration when needed, disables RAM discard, sets initial virtio status, and installs the custom memory listener.
- Shadow virtqueues: `vhost_vdpa_svqs_start()`, `vhost_vdpa_svqs_stop()`, `vhost_vdpa_svq_map_rings()`, and helper routines map SVQ driver/device areas into vDPA IOVA space and substitute SVQ kick/call fds.
- Device start/stop: `vhost_vdpa_dev_start()` initializes host notifiers and SVQs, registers the memory listener in the active DMA address space, and sets `DRIVER_OK`; stop suspends or resets and tears down SVQ/notifier state.
- Exported backend table: `vdpa_ops` wires this file into generic `vhost.c` through callbacks for feature negotiation, mem table validation, vring operations, config access, reset, IOMMU forcing, and device status.

## Dependencies
Uses Linux `vhost.h`, `vfio.h`, eventfd/ioctl/mmap APIs, QEMU memory listeners, IOMMU notifiers, `VhostShadowVirtqueue`, `VhostIOVATree`, migration blockers, RAM discard controls, and tracepoints. It depends heavily on generic vhost lifecycle contracts from `hw/virtio/vhost.h`.

## Behavior/Risks
- Only RAM or IOMMU regions are accepted; protected memory, RAM devices, MMIO, out-of-range IOVAs, and unaligned page mappings are skipped or reported.
- `shadow_data` mode allocates GPA-to-IOVA mappings and must remove partially inserted mappings on failure.
- SVQ is explicitly rejected when a virtio IOMMU is enabled, because the implementation cannot combine those modes.
- Full 64-bit unmap size is split because the unmap ioctl cannot accept a full 64-bit size.
- Many operations are first-device or last-device gated to avoid repeating shared vDPA state changes across queue-pair split devices.
- Stop prefers `VHOST_VDPA_SUSPEND` when supported; otherwise reset is used, which affects whether vring base can be trusted later.
