# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ondisk.c

## Purpose
Handles HAMMER2 block-device vnode lookup/open/close, device list initialization/cleanup, volume-header reading, volume validation, and logical offset to volume lookup.

## Device Lifecycle
`hammer2_lookup_device()` resolves a device path. Root mounts use `kgetdiskbyname()` and `bdevvp()`, while normal mounts use `nlookup()` and `cache_vref()`. It validates the vnode is a block device with `vn_isdisk()`.

`hammer2_init_devvp()` parses colon-separated block-device strings, prepends `/dev/` for relative paths, looks up each device vnode, and appends `hammer2_devvp_t` entries. `hammer2_cleanup_devvp()` clears `si_mountpoint`, releases vnodes, frees path strings, and frees list entries.

`hammer2_open_devvp()` refuses already-referenced devices via `vcount()`, invalidates buffers, then opens each vnode read-only or read-write. `hammer2_close_devvp()` invalidates/saves buffers and closes open device vnodes.

## Volume Validation
`hammer2_read_volume_header()` scans the four HAMMER2 volume-header zones, reads each candidate header, checks magic, rejects reverse-endian filesystems, verifies all header CRC sections, and returns the valid header with the highest `mirror_tid`.

`hammer2_init_volumes()` initializes the `volumes[]` table, reads each supplied device’s volume header, checks version/nvolume/fsid/fstype consistency, records id/offset/size, captures root volume data and zone, and sets `si_mountpoint`.

`hammer2_verify_volumes_common()` validates root volume id, HAMMER2 UUID, initialized volume fields, device media sizes, and nonzero sizes. `hammer2_verify_volumes_1()` enforces legacy single-volume layout fields. `hammer2_verify_volumes_2()` enforces multi-volume count, total size, ordered ids, contiguous offsets, and required alignment.

## Offset Mapping
`hammer2_get_volume()` masks off radix bits, scans mounted volumes for the offset range, and panics if no volume owns the offset. Current code comments say locking is unnecessary until volume-add support exists.

## Risk Notes
Mount correctness depends on strict header CRC and layout checks. Multi-volume support assumes volumes are ordered and contiguous. Reverse-endian media is detected but unsupported.
