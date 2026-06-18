# File Research: sources/os/linux/linux-stable/fs/jffs2/build.c

## Scope
Implements JFFS2 mount-time filesystem build from scanned flash nodes, including inode-cache link counting, dead inode removal, temporary dirent cleanup, xattr subsystem build, trigger-level calculation, and eraseblock list initialization.

## Primary APIs
The exported entry point is `jffs2_do_mount_fs()`. Internal helpers include inode-cache iteration helpers, `jffs2_build_inode_pass1()`, `jffs2_build_filesystem()`, `jffs2_build_remove_unlinked_inode()`, and `jffs2_calc_trigger_levels()`.

## Behavior
`jffs2_do_mount_fs()` initializes eraseblock accounting from flash/sector size, allocates the eraseblock array with `vzalloc()` or `kzalloc()`, initializes all block lists, starts summary support, builds the filesystem, and computes space reservation thresholds.

`jffs2_build_filesystem()` sets scanning/building flags, calls `jffs2_scan_medium()`, then pass 1 walks directory scan dirents and increments child inode link counts. Missing child inode caches cause the dirent raw node to be marked obsolete.

Pass 2 removes inode caches with zero link count by marking all raw nodes obsolete. If such an inode is a directory, child link counts are decremented and newly unlinked children are queued for iterative removal via `dead_fds`.

After dead cleanup, directory hardlink detection is revisited. Temporary `scan_dents` are freed, and directory child inode caches store parent inode numbers in `pino_nlink`. Then the xattr subsystem is built, lists are rotated for wear leveling, and build flags are cleared.

`jffs2_calc_trigger_levels()` computes reserved eraseblock thresholds for deletion, writes, GC wakeup, GC merge, bad-block GC, very-dirty GC triggering, and minimum dirty space needed for useful GC.

## State And Data
Touches `free_size`, `nr_blocks`, `blocks[]`, eraseblock lists, `highest_ino`, summary state, `JFFS2_SB_FLAG_SCANNING`, `JFFS2_SB_FLAG_BUILDING`, inode-cache `pino_nlink`, `scan_dents`, flags, and reservation thresholds.

## Dependencies
Depends on medium scanning, raw node obsoletion, inode cache lookup/free, full-dirent allocation/free, xattr subsystem build/clear, summary init/exit, eraseblock management, wear-level list rotation, and MTD sizing.

## Risks And Invariants
Mount reconstruction relies on physical scan results plus dirent link counts. Dead directory cleanup is iterative to avoid recursion. Directory hardlinks are treated as anomalous and warned after dead entries are removed. Failure paths must free temporary dirents, xattrs, summary state, raw refs, inode caches, and block arrays.
