# File Research: sources/os/linux/linux/fs/ceph/ioctl.h

## Purpose

`ioctl.h` defines the userspace ABI for CephFS-specific ioctl commands and their argument structures.

## ABI Definitions

`CEPH_IOCTL_MAGIC` is `0x97`.

`struct ceph_ioctl_layout` contains:

- `stripe_unit`
- `stripe_count`
- `object_size`
- `data_pool`
- obsolete `preferred_osd`, now ignored on set and returned as `-1`

Layout ioctls:

- `CEPH_IOC_GET_LAYOUT`: get file layout or directory layout policy.
- `CEPH_IOC_SET_LAYOUT`: set layout on a newly created file before data is written.
- `CEPH_IOC_SET_LAYOUT_POLICY`: set default layout policy on a directory for future children.

`struct ceph_ioctl_dataloc` contains input/output data for locating a file offset in the Ceph object store:

- input `file_offset`;
- output object offset, object number, object size, object name;
- output block offset and block size;
- output primary OSD id and address.

`CEPH_IOC_GET_DATALOC` is an in/out ioctl over that structure.

Mode ioctls:

- `CEPH_IOC_LAZYIO`: relax normal multi-client consistency and permit buffered I/O when the application accepts it.
- `CEPH_IOC_SYNCIO`: force synchronous I/O that bypasses page cache, similar to O_DIRECT but without the same alignment and copy constraints.

## Integration Notes

This header is included by `ioctl.c` and is part of the CephFS user ABI. Structure layout uses 64-bit fields for sane alignment across architectures, so changes require ABI care.

## Risks

- `CEPH_IOC_SET_LAYOUT_POLICY` and `CEPH_IOC_SYNCIO` both use ioctl number `5` with the same magic but different encoding direction/size. This is visible in the header and must remain understood by the dispatcher and userspace ABI compatibility expectations.
- Comments describe legacy behavior, especially `preferred_osd`; implementation must keep returning `-1` and ignoring set values.
