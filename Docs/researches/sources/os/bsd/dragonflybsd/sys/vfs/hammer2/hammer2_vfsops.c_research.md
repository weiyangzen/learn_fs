# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vfsops.c

## Purpose
Main HAMMER2 VFS operations implementation for DragonFlyBSD. It defines filesystem module init/uninit, mount/remount/unmount, PFS allocation/freeing, root/vget/stat/export operations, mount-time recovery, sync/flushing, write-pressure throttling, volume-data modification, and ENOSPC heuristics.

## Globals And Init
The file owns global mount/PFS lists, mount lock, sysctls, counters, malloc types, and VFS operation table. `hammer2_vfs_init()` sizes XOP worker groups from `ncpus`, sets DIO cache limits, verifies on-disk structure sizes, creates object caches for compression/decompression buffers and XOPs, initializes global lists/locks, and derives dirty-chain/dirty-inode limits. `hammer2_vfs_uninit()` destroys caches.

## PFS Lifecycle
`hammer2_pfsalloc()` finds or creates a PFS by cluster id or forced-local name, initializes transaction management, inode allocator, locks, queues, hashes, root inode, cluster slots, PFS type/name/hmp arrays, visible master counts, sync threads, and XOP helpers. `hammer2_pfsdealloc()` removes one cluster element and deletes associated sync/XOP threads. `hammer2_pfsfree()` tears down a PFS when no cluster chains remain. `hammer2_pfsfree_scan()` removes all references to an unmounted device from PFS/SPMP lists, freezing management threads while it edits embedded clusters.

## Mount Flow
`hammer2_vfs_mount()` handles root mounts, new mounts, secondary label-only mounts, and remount updates. It copies `hammer2_mount_info`, parses `device@label`, defaults labels from partition suffix, initializes device vnodes, matches existing mounted devices, opens new devices, initializes volume metadata, constructs the `hammer2_dev_t`, embedded volume chain and freemap chain, creates the super-root PFS, locates the super-root inode, runs recovery/fixup on writable mounts, initializes cluster I/O and bulkfree, optionally reconnects a cluster fd, then finds and attaches the requested PFS to `mp`.

`hammer2_remount()` supports read-only to read-write transition by reopening volumes writable, running recovery/fixup on the root volume, then updating `hmp`/PFS read-only state.

## Unmount Flow
`hammer2_vfs_unmount()` flushes vnodes and runs three syncs for clean teardown, cleans XOP helpers, and calls `hammer2_unmount_helper()`. The helper either detaches a PFS mount and decrements device mount counts, or fully decommissions a device: shuts down network and bulkfree, removes PFS references, flushes freemap and volume chains, closes/cleans device vnodes, clears modified flags, dumps chains for diagnostics, drops embedded chains, cleans DIO hashes, removes the mount list entry, and frees device allocators.

## Lookup, Root, Stat, Export
`hammer2_vfs_vget()` resolves inode numbers from cache or by XOP lookup under iroot. `hammer2_vfs_root()` initializes PFS inode/modify transaction counters from the root cluster if needed and returns the root vnode. `hammer2_vfs_statfs()` and `hammer2_vfs_statvfs()` report blocks/free space/files from the mounted PFS’s backing device and reserve 5% from non-root availability. `hammer2_vfs_vptofh()` and `hammer2_vfs_fhtovp()` implement simple file-handle conversion by inode number. `hammer2_vfs_checkexp()` uses `vfs_export_lookup()` for NFS export checks.

## Recovery And Fixups
`hammer2_recovery()` compares `freemap_tid` with `mirror_tid` and scans committed topology to mark newly referenced blocks allocated after a crash. `hammer2_recovery_scan()` recursively scans volume/inode/indirect topology with a depth-defer list and adjusts freemap state for blockrefs newer than the freemap sync tid. `hammer2_fixup_pfses()` corrects older media where PFSROOT blockref flags were lost after moving PFS inodes into indirect blocks.

## Sync And Throttling
`hammer2_vfs_sync_pmp()` moves dependency/side queues to syncq, carefully avoids vnode/inode deadlocks with `vget(... LK_NOWAIT)`, flushes dirty buffers and inode chains, restarts for PASS2/dependency cases, then flushes the PFS root last with `HAMMER2_XOP_VOLHDR` so volume headers and root blocksets update correctly. It waits for strategy BIO completion before ending the flush transaction.

`hammer2_lwinprog_ref/drop/wait()` throttle outstanding logical writes. `hammer2_vfs_modifying()` rejects writes on read-only mounts and calls `hammer2_pfs_memory_wait()`. Dirty memory helpers trigger async syncer work and sleep/wake with hysteresis based on dirty-chain and dirty-inode limits.

## Volume And Space Helpers
`hammer2_voldata_lock/unlock()` wrap the volume lock. `hammer2_voldata_modify()` marks the embedded volume chain modified and advances its mirror TID. `hammer2_vfs_enospace()` caches free-space values per tick across master/soft-master cluster members and returns warning/severe states based on root versus non-root reserve thresholds.

## Risk Notes
This file coordinates nearly all high-level HAMMER2 lifetimes. The riskiest areas are mount failure unwinding, PFS/device reference accounting, sync queue restart logic, and lock ordering around vnode/inode flushes. The code intentionally uses repeated syncs and recovery scans to handle delayed freemap consistency.
