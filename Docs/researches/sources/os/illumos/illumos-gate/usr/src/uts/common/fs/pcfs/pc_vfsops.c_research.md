# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vfsops.c

PCFS module, VFS operation, mount, unmount, FAT loading/syncing, media geometry, partition parsing, and BPB validation implementation.

Key responsibilities:
- Registers the PCFS filesystem module and creates file/directory vnode operation vectors during `pcfsinit()`.
- Defines mount options for hidden-file exposure, case folding, timestamp clamping, access-time updates, timezone, and sector-size override.
- Implements mount path resolution and PCFS drive suffix parsing in `pcfs_device_identify()`, supporting suffixes like `:boot`, numeric logical drives, and drive letters.
- Prevents duplicate mounts with logical-drive-aware pseudo device numbers in `pcfs_device_ismounted()`.
- Performs `pcfs_mount()`, including policy checks, device open, mount-option parsing, FAT type detection, BPB validation, FAT verification, VFS initialization, and mount table insertion.
- Handles unmount and forced unmount through `pcfs_unmount()` and delayed cleanup through `pcfs_freevfs()`.
- Implements VFS root, statvfs, sync, syncfs, vget, and lock/unlock operations.
- Loads, validates, caches, invalidates, and syncs FAT copies through `pc_getfat()`, `pc_readfat()`, `pc_writefat()`, `pc_syncfat()`, and FAT change-map helpers.
- Parses fdisk primary, extended, extra, and boot partitions through `findTheDrive()`.
- Detects FAT12/FAT16/FAT32 geometry and validity through `parseBPB()` and `secondaryBPBChecks()`.
- Detects device sector size, removable/hotpluggable/floppy behavior, and default noatime policy through `pcfs_device_getinfo()`.

Dependencies:
- Uses illumos VFS, vnode, modctl, LDI, DKIO, fdisk, buffer cache, mount option, policy, DTrace, and PCFS on-disk layout infrastructure.
- Depends on vnode/node/dir/allocation routines for root lookup, vget, sync, and teardown.

Notable risks:
- `findTheDrive()` explicitly cannot address disks beyond 2 TB because it uses `daddr_t` and 32-bit fdisk fields.
- BPB parsing is intentionally tolerant of real-world malformed FAT media, but still must prevent divide-by-zero, overflow, and panic on malicious filesystems.
- FAT alternate-copy mismatch can be warning-only unless the primary FAT signature is already suspicious.
- Forced unmount and irrecoverable-state handling rely on correct global lock ordering: `pcfslock > pcfs_lock > pcnodes_lock`.
- FAT sync writes all FAT copies but only changed FAT chunks for FAT12/16/32 via the change map.
