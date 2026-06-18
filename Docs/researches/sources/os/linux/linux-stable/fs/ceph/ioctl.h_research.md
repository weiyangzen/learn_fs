# File Research: sources/os/linux/linux-stable/fs/ceph/ioctl.h

## Role

`ioctl.h` defines the CephFS userspace ioctl ABI consumed by `ioctl.c`.

## Constants

`CEPH_IOCTL_MAGIC` is `0x97`.

## Layout ABI

`struct ceph_ioctl_layout` contains:

- `stripe_unit`
- `stripe_count`
- `object_size`
- `data_pool`
- obsolete `preferred_osd`

All main fields use `__u64` for cross-architecture alignment. `preferred_osd` is obsolete; new values are ignored and returned as `-1`.

Defined layout commands:

- `CEPH_IOC_GET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT_POLICY`

The comments document that file layouts control object striping and data pool selection; directory layout policy applies to future children, not retroactively.

## Data Location ABI

`struct ceph_ioctl_dataloc` is an in/out structure for mapping a file offset to object and OSD location data.

Fields include:

- input/output `file_offset`
- output object offset, object number, object size, object name
- output block offset and block size
- output OSD id
- output OSD address as `sockaddr_storage`

Defined command:

- `CEPH_IOC_GET_DATALOC`

## Consistency Control Ioctls

`CEPH_IOC_LAZYIO` relaxes consistency for a file descriptor so buffered I/O may be used when the application accepts weaker cross-client consistency.

`CEPH_IOC_SYNCIO` forces synchronous I/O behavior that bypasses page cache in cases similar to multi-client write sharing. The comment distinguishes it from `O_SYNC`/`O_DSYNC` and notes similarity to `O_DIRECT` without the same alignment and stable-page constraints.

## Notable ABI Detail

Both `CEPH_IOC_SET_LAYOUT_POLICY` and `CEPH_IOC_SYNCIO` use command number `5` with the same magic but different ioctl direction/argument encoding. This is existing ABI encoded through `_IOW` versus `_IO`.
