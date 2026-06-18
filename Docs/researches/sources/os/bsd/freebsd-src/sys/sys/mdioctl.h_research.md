# File Research: sources/os/bsd/freebsd-src/sys/sys/mdioctl.h

Defines ioctl ABI for the FreeBSD memory disk pseudo-device.

Key content:
- `enum md_types` covers memory-disk backing types: malloc, preload, vnode, swap, and null.
- `struct md_ioctl` carries version, unit number, type, backing file path, media size, sector size, options, base address, firmware geometry, label, and padding.
- Device names: `MD_NAME` = `md`, `MDCTL_NAME` = `mdctl`.
- `MDIOVERSION` is 0.
- Ioctls:
  - `MDIOCATTACH`
  - `MDIOCDETACH`
  - `MDIOCQUERY`
  - `MDIOCRESIZE`
- Options include clustering behavior, swap reservation, auto unit, readonly, compression, force, async, vnode verify, cache vnode data, and BIO_DELETE deallocation requirement.

Research relevance:
- Directly relevant to block-storage and filesystem test setups: md devices provide in-memory, file-backed, swap-backed, preload-backed, or null block devices.
- Vnode-backed options intersect with VFS caching, verification, and BIO_DELETE behavior.

Cautions:
- Comment notes configuration persists across opens/closes until cleared/detached.
- `MD_CLUSTER` comment says "Don't cluster", so the flag name is historically counterintuitive.
