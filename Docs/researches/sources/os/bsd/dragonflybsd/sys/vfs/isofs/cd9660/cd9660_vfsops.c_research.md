# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vfsops.c

## Scope

Implements the CD9660 VFS layer: mount, root mount, unmount, root vnode lookup, statfs, NFS export/filehandle conversion, vnode construction, and module registration.

## APIs And Behavior

- Registers `cd9660_vfsops` as a read-only local filesystem.
- `iso_get_ssector()` scans CD TOC data to mount the last data track of multisession media.
- `cd9660_mount()` handles root mounts, user argument copyin, read-only enforcement, export updates, device lookup, permission checks, and mount-from stat updates.
- `iso_mountfs()` opens the block device, scans volume descriptors, detects High Sierra, primary, supplementary/Joliet descriptors, validates logical block size, initializes `iso_mnt`, checks Rock Ridge support, opens iconv conversion handles, chooses ISO/RRIP/Joliet mode, and installs vnode operation tables.
- `cd9660_unmount()` flushes vnodes, closes iconv handles, clears the device mountpoint, closes/releases the device vnode, and frees mount state.
- `cd9660_root()`, `cd9660_vget()`, and `cd9660_vget_internal()` construct or find ISO vnodes and initialize type, attributes, size, VM object, aliases, and root flags.
- `cd9660_fhtovp()`, `cd9660_vptofh()`, and `cd9660_checkexp()` support NFS filehandles and exports.

## Dependencies

Uses DragonFly VFS, vnode, buffer, CD ioctl, device, nlookup, iconv, netexport, and CD9660 node/RRIP helpers.

## Risks And Invariants

Mounts are always read-only. Volume descriptor scanning assumes 2048-byte descriptor sectors. Vnode construction validates pseudo-inode block range and record boundaries before trusting directory records. Rock Ridge root handling may require reading the relocated `.` record.
