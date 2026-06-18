# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.h

## Purpose
Defines the HAMMER2 user/kernel ioctl ABI for administrative operations: version query, remote copy configuration, socket association, PFS management, inode metadata access, bulkfree, destructive deletion, emergency mode, growfs, and volume listing.

## Public ABI
The file exports fixed C structs used directly with `_IOWR('h', ...)` ioctl numbers:
- `hammer2_ioc_version`: returns filesystem ioctl version.
- `hammer2_ioc_recluster`: passes an fd for recluster operations.
- `hammer2_ioc_remote`: manages `volume->copyinfo[]` entries and socket descriptors. Carries `copyid`, iteration `nextid`, fd, and two `hammer2_volconf_t` copies for replace/rename-like operations.
- `hammer2_ioc_pfs`: describes PFS entries under the super-root, including name hash cursor fields, PFS type/subtype/flags, fsid, clid, and label.
- `hammer2_ioc_inode`: gets/sets inode data and optional quota/copy/check/compression flags.
- `hammer2_ioc_bulkfree`: parameters and counters for bulkfree scans.
- `hammer2_ioc_destroy`: unconditional delete by path or inode number.
- `hammer2_ioc_growfs`: grow filesystem target size and modified flag.
- `hammer2_ioc_volume` / `hammer2_ioc_volume_list`: expose multi-volume path/id/offset/size information.

## Constants And Commands
Important flags include `HAMMER2_PFSFLAGS_NOSYNC` and inode ioctl flags for inode quota, data quota, copies, check algorithm, and compression algorithm. Ioctl command numbers currently span version/recluster at 64-65, remotes at 68-71, sockets at 76-77, PFS operations at 80-84, inode get/set at 86-87, debug/bulkfree/destroy/emergency/growfs/volume-list at 91-97. Numbers 88-90 are explicitly reserved for old compression ioctls.

## Dependencies
Includes `sys/param.h`, `sys/syslimits.h`, `sys/ioccom.h`, `hammer2_disk.h`, and `hammer2_mount.h`, so this header binds the ioctl ABI to on-disk structures and mount flags.

## Integration Notes
The structures are ABI-sensitive: several include reserved padding or fixed arrays, and userland HAMMER2 tools must match them exactly. Any changes require compatibility review. `HAMMER2IOC_DESTROY` is explicitly dangerous because it deletes unconditionally.
