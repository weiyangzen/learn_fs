# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_vfsops.c

Read completely: 850 lines.

Purpose: implements FreeBSD `cd9660` VFS mount-layer operations for ISO9660 media, including mount argument translation, GEOM-backed device opening, volume descriptor parsing, root vnode lookup, statfs, file-handle conversion, and vnode construction.

Key entry points:
- `cd9660_cmount()` converts legacy `struct iso_args` into kernel mount options such as `from`, `uid`, `gid`, masks, `ssector`, RRIP/Joliet/kiconv toggles.
- `cd9660_mount()` forces read-only mounts, resolves the block device, verifies access or mount privilege, and either calls `iso_mountfs()` or validates updates.
- `iso_mountfs()` is the core mount routine: opens the device through GEOM, validates sector/logical block sizes, scans volume descriptors from sector `16 + ssector`, recognizes primary, supplementary/Joliet, High Sierra, and end descriptors, initializes `struct iso_mnt`, applies mount options, detects RRIP, handles kiconv, and selects filesystem type.
- `cd9660_unmount()` flushes vnodes, closes iconv handles, closes GEOM consumer, releases device vnode/cdev refs, and frees mount state.
- `cd9660_root()`, `cd9660_statfs()`, `cd9660_fhtovp()`, `cd9660_vget()`, and `cd9660_vget_internal()` provide VFS root/stat/filehandle/vnode lookup behavior.

Important data flow:
- `mp->mnt_data` is set to an allocated `struct iso_mnt` only after descriptor and block-size validation.
- Root directory record data is copied from the selected primary or Joliet descriptor into `isomp->root`.
- RRIP support is detected by reading the root directory block and calling `cd9660_rrip_offset()`.
- NFS filehandles use `struct ifid` and feed back into `VFS_VGET()`.

Concurrency/lifetime notes:
- Vnode creation uses `vfs_hash_get()`/`vfs_hash_insert()` with a custom 64-bit inode comparator.
- `cd9660_vget_internal()` allows duplicate vnode creation races and resolves them through the hash insertion result.
- Error paths carefully release buffers, GEOM consumer, `iso_mnt`, and device references.

Research notes:
- Mounts are always read-only and local.
- Joliet is used only when RRIP is not active.
- The inode scheme is constrained by 32-bit `ino_t` assumptions noted in comments for NFS/export cases.
