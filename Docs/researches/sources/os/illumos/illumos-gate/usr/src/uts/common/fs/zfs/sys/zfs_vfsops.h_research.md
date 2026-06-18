# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_vfsops.h

Defines mount-wide ZFS filesystem state (`zfsvfs_t`), NFS filehandle formats, quota/user accounting entry points, and filesystem lifecycle helpers.

Key elements:
- `zfsvfs_t` stores VFS pointer, parent filesystem, objset, root/unlinked objects, max block size, FUID state, ZIL pointer, ACL settings, case/UTF-8/normalization settings, atime, teardown locks, znode lists, root/control vnodes, snapshot and SA/FUID flags, quota object IDs, replay state, SA attribute table, znode hold mutexes, and unlink-drain task.
- `zfid_short_t` and `zfid_long_t` encode normal and snapshot filehandles under object/generation/objset size constraints.
- Defines `SHORT_FID_LEN` and `LONG_FID_LEN`.

Main dependencies and interactions:
- Includes VFS, ZIL, SA, rrwlock, ioctl, and DSL dataset headers.
- Used by znode, control directory, FUID, quota, mount, suspend/resume, and temporary property code.

Implementation notes:
- Filehandle layout is constrained by NFSv2/NFSv3 historical limits and DMU 48-bit object IDs.
- `ZFS_OBJ_MTX_SZ` controls the hash table used by znode object-hold locks.
