# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zvol.h

Declares ZFS volume constants and kernel block-device entry points.

Key elements:
- `ZVOL_OBJ` and `ZVOL_ZAP_OBJ` identify volume object slots.
- Declares volume size/blocksize validation, stats, creation callback, minor create/remove, volume resize, and busy/init/fini.
- Declares device operations: open, close, dump, strategy, read/write, async read/write, ioctl.
- Declares helper accessors for volume params, size, write-cache-enable setting, and minor-based ZIL write logging.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Integrates ZFS objsets with illumos block device interfaces and ZIL logging.

Implementation notes:
- The params accessor returns opaque handles for minor, objset, ZIL, range lock, and bonus state.
