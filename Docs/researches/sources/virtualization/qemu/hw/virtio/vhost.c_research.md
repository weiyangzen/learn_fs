# File Research: sources/virtualization/qemu/hw/virtio/vhost.c

## Purpose
Provides QEMU's generic vhost core shared by kernel, vhost-user, and vhost-vDPA backends. It manages backend selection, memory tables, dirty logging, notifier handoff, virtqueue setup/teardown, IOMMU invalidation, migration blockers, inflight buffers, and backend state transfer.

## Key Elements
- Global state tracks all vhost devices, per-backend shared dirty log buffers, and elected dirty-log scanners.
- Memory slot helpers `vhost_get_max_memslots()` and `vhost_get_free_memslots()` summarize backend memory table limits across active devices.
- Dirty logging: `vhost_dev_sync_region()`, `vhost_sync_dirty_bitmap()`, `vhost_log_get()`, `vhost_log_put()`, and `vhost_dev_log_resize()` maintain vhost dirty bitmaps and mark QEMU memory dirty during migration.
- Backend selection: `vhost_set_backend_type()` installs `kernel_ops`, `user_ops`, or `vdpa_ops` based on build-time support.
- Memory listener: `vhost_begin()`, `vhost_region_add_section()`, `vhost_region_addnop()`, and `vhost_commit()` collect RAM sections, merge compatible neighbors, rebuild `struct vhost_memory`, verify ring mappings, and update backend memory tables.
- IOMMU listener: `vhost_iommu_region_add()`, `vhost_iommu_region_del()`, and `vhost_iommu_unmap_notify()` invalidate backend IOTLB entries when translated mappings disappear.
- Virtqueue lifecycle: `vhost_virtqueue_init()`, `vhost_virtqueue_start()`, `vhost_virtqueue_stop()`, and `do_vhost_virtqueue_stop()` configure vring size/base/endian/address/kick/call fds and keep QEMU queue indices synchronized.
- Notifier handoff: `vhost_dev_enable_notifiers()` grabs ioeventfd ownership and assigns host notifiers; `vhost_dev_disable_notifiers()` reverses it.
- Device lifecycle: `vhost_dev_init()`, `vhost_dev_start()`, `vhost_dev_stop()`, `vhost_dev_force_stop()`, and `vhost_dev_cleanup()` compose backend ops, memory listeners, migration blockers, vring enable, config interrupts, logging, and IOMMU listeners.
- Migration support includes VMState descriptions for inflight buffers and `vhost_save_backend_state()` / `vhost_load_backend_state()` pipe-based backend state transfer.

## Dependencies
Uses QEMU memory API, address-space mapping, RAMBlock helpers, migration blockers and QEMUFile, memfd, virtio bus/device APIs, Linux vhost type headers, DMA/IOMMU APIs, and per-backend `VhostOps`.

## Behavior/Risks
- Memory region selection excludes ROM and unsupported dirty-log users; vhost-user may require fd-backed shared RAM and reject private memslots.
- Dirty logging uses a per-backend shared log and elects one device to scan memory sections to avoid duplicate scanning.
- Runtime memory table changes can abort on ring mapping verification failure.
- `vhost_dev_init()` rejects configurations where memory device auto-sizing assumed more memslots than the backend can support.
- vhost-user disconnects can alter state during logging setup, so migration-log code checks whether the device stopped while communicating with the backend.
- State transfer asserts the device is stopped while saving/loading backend state.
