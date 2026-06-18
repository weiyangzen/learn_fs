# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_disk.c

## Role

`vdev_disk.c` implements the kernel disk-backed leaf vdev operations using illumos LDI. It opens block devices, tracks devid/minor/path identity, registers LDI offline/degrade callbacks, issues physical reads/writes, cache flushes, TRIM, dump I/O, and pre-root device discovery for root-pool import.

## Main Behavior

Disk state:
- `vdev_disk_t` stores the decoded devid, minor name, LDI handle, registered LDI callback IDs, and an offline flag.
- `vdev_disk_bypass_devid` can deliberately ignore stored devids for recovery.
- `zfs_no_trim` disables TRIM globally.
- `zfs_nocacheflush` skips volatile write-cache flushes for debugging/performance analysis but is explicitly unsafe on power loss.

Open and identity:
- `vdev_disk_open()` requires an absolute path.
- It tries to open by user path first, with legacy whole-disk `s0` path repair if needed.
- It validates the opened device against the stored devid, then falls back to opening by devid, physical path, logical path, or pre-root alternate path.
- It can force a specific pre-root root-disk path through `vdev_disk_preroot_force_path()`.
- After opening, it may update or remove stored devid/minor values and refresh `vdev_physpath`.
- It registers LDI callbacks for offline and degrade events.
- It obtains physical size, media logical/physical block size, ashift, whole-disk maximum expansion size, write-cache enablement, TRIM support, and non-rotational property.

Close and callbacks:
- `vdev_disk_close()` frees devid/minor state, closes the LDI handle, removes callback registrations, and frees `vdev_tsd`.
- Offline notify marks `vd_ldi_offline`, posts removal, sets `vdev_remove_wanted`, and requests `SPA_ASYNC_REMOVE`.
- Offline finalize requests a probe if offline failed.
- Degrade finalize marks the vdev degraded.

I/O:
- `vdev_disk_io_start()` handles:
  - `DKIOCFLUSHWRITECACHE` using async `struct dk_callback`, unless disabled or known unsupported.
  - `ZIO_TYPE_TRIM` through `DKIOCFREE`, disabling future TRIM if unsupported.
  - normal reads/writes through `ldi_strategy()` with ABD-borrowed buffers.
- `vdev_disk_io_intr()` normalizes completion errors to `EIO`, treats residuals as errors, returns ABD buffers, frees the wrapper, and delays zio interrupt.
- `vdev_disk_io_done()` probes device state on EIO and schedules async removal or delayed close.
- `vdev_disk_dumpio()` supports crash-dump paths with `ldi_dump()` and normal dump I/O via synchronous physio.

Root-label and pre-root discovery:
- `vdev_disk_read_rootlabel()` opens a device by devid or path, reads labels, unpacks a valid config nvlist, and rejects destroyed or txg-zero labels.
- Pre-root scanning walks available block devices, records pool GUID/vdev GUID to devpath mappings, and allows lookup during early boot.
- `vdev_disk_preroot_init()` and `vdev_disk_preroot_fini()` manage the pre-root cache.

## Integration Notes

This file is the illumos-specific physical disk adapter for the generic vdev layer. It depends on LDI, DKIO ioctls, device identifiers, FMA removal/degrade paths, ABD buffer borrowing, ZIO completion, root-label config reading, and pre-root block-device walking.

## Risk Notes

- Device identity ordering is deliberate: path preserves administrator intent, devid survives recabling, and label validation happens at higher layers.
- Devid bypass permanently stops storing devid information for imported pools.
- `zfs_nocacheflush` can corrupt pools on power loss with volatile out-of-order write caches.
- TRIM support is mutable; failed `DKIOCFREE` can disable it for the vdev.
- Residual I/O counts are treated as hard errors.
- LDI offline can race with ordinary I/O; `vd_ldi_offline` prevents new work after notification.
- Pre-root scanning is best effort and intentionally ignores many invalid-label devices.
