# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfsmount.h

## Role

Defines the MSDOSFS mount control block, mount arguments, mount flags, and core block/cluster/offset conversion macros used by FAT vnode, lookup, FAT, and mount code.

## Main Data Structures

- `struct msdosfsmount` stores the DragonFly mount pointer, synthetic uid/gid/masks, backing device vnode/device, BPB fields, FAT/root/cluster geometry, free-space state, FAT in-use bitmap, mount flags, export state, and optional iconv handles.
- `struct msdosfs_args` is the userspace mount argument ABI: device path, export args, uid/gid/masks, mount flags, charset names, and directory mask.

## Important Macros

- `VFSTOMSDOSFS(mp)` extracts the filesystem mount object from `mnt_data`.
- `FATOFS(pmp, cn)` computes a cluster’s byte offset within the FAT.
- `bptoep()` converts a buffer and directory offset into a `struct direntry *`.
- `de_bn2cn()`, `de_cn2bn()`, `de_cluster()`, `de_clcount()`, `de_blk()`, `de_cn2off()`, `de_bn2off()`, `de_bn2doff()`, and `de_cn2doff()` perform block, cluster, and byte-offset conversions.
- `cntobn()` maps FAT cluster numbers to filesystem-relative block numbers.
- `roottobn()` and `detobn()` map directory-entry locations to backing blocks.
- `DOINGASYNC(vp)` checks the mount async flag.
- `ASSERT_VOP_LOCKED()` and `ASSERT_VOP_ELOCKED()` wrap DragonFly vnode lock assertions.

## Mount Flags

- User-visible options include `MSDOSFSMNT_SHORTNAME`, `MSDOSFSMNT_LONGNAME`, `MSDOSFSMNT_NOWIN95`, and `MSDOSFSMNT_KICONV`.
- Internal flags include `MSDOSFSMNT_RONLY`, `MSDOSFSMNT_WAITONFAT`, `MSDOSFS_FATMIRROR`, and `MSDOSFS_FSIMOD`.

## Implementation Notes

- BPB fields are exposed through shorthand macros such as `pm_BytesPerSec`, `pm_FATs`, `pm_RootDirEnts`, and `pm_HugeSectors`.
- `pm_BlkPerSec` captures physical-sector-to-`DEV_BSIZE` scaling and is folded into most geometry fields at mount time.
- Root directory handling is macro-level special-cased because pre-FAT32 root directories are fixed regions, not normal cluster chains.
- `MSDOSFS_LOCK_MP()` and related macros are currently no-ops in this header, so mount-level serialization must come from surrounding code or single-threaded assumptions.

## Dependencies

Included by MSDOSFS mount, vnode, lookup, denode, FAT, and makefs-related code. It depends on FAT BPB definitions, DragonFly mount/vnode/device types, netexport for kernel builds, and iconv constants for mount charset fields.

## Research Notes

This header is the in-memory geometry contract for the MSDOSFS implementation. Errors in these conversions would affect lookup, read/write, FAT allocation, directory mutation, and export file handles.
