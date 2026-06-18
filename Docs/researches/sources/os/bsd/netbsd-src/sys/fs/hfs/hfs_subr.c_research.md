# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_subr.c

## Purpose
Provides HFS vnode initialization, kernel callback adapters for `libhfs`, physical block reads, HFS time conversion, endian cursor helpers, and catalog-record-to-vnode-type mapping.

## Main Entry Points
- `hfs_vinit()` derives vnode type from the catalog record, switches special/fifo vnodes to the right operation vectors, initializes special devices, and marks the root vnode.
- `hfs_libcb_error()`, `hfs_libcb_malloc()`, `hfs_libcb_realloc()`, and `hfs_libcb_free()` adapt `libhfs` diagnostics and memory allocation to the kernel.
- `hfs_libcb_opendev()` uses the already-resolved block device vnode, opens it with read or read/write mode, invalidates stale buffers, records device block size, and stores callback data on the volume.
- `hfs_libcb_closedev()` closes the stored device vnode and frees callback data.
- `hfs_libcb_read()` translates volume-relative reads into device vnode reads through `hfs_pread()`.
- `hfs_pread()` performs sector-aligned buffer-cache reads and copies the requested byte range out of larger device blocks.
- `hfs_time_to_timespec()` converts HFS+ seconds since 1904 to Unix `timespec`.
- `be16tohp()`, `be32tohp()`, and `be64tohp()` read big-endian values while advancing a pointer.
- `hfs_catalog_keyed_record_vtype()` maps catalog file mode or folder records to NetBSD `enum vtype`.

## Dependencies
Uses NetBSD vnode, buffer cache, kauth, device-size helpers, specfs, and HFS structures from `hfs.h`.

## Risks and Notes
The callback allocator still uses `M_TEMP` in places marked as needing pools. `hfs_pread()` has an in-source comment questioning behavior when the aligned sector start differs from the requested offset. Dates before 1970 are clamped to the Unix epoch. `hfs_catalog_keyed_record_vtype()` assumes non-file records are directories.
