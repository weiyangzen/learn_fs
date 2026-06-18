# File Research: sources/os/linux/linux/fs/jffs2/build.c

## Role

`build.c` builds JFFS2 in-memory filesystem structures at mount time after scanning flash. It initializes eraseblock state, scans raw nodes, reconstructs inode and directory link relationships, removes unlinked inode trees, initializes xattr state, computes GC reservation thresholds, and performs final list rotation for wear leveling.

## Mount Entry Point

`jffs2_do_mount_fs()`:
- Initializes free size and block count from flash/sector size.
- Allocates the eraseblock array with `vzalloc()` or `kzalloc()`.
- Initializes each eraseblock offset and free size.
- Initializes all eraseblock state lists.
- Sets `highest_ino`, initializes summary support with `jffs2_sum_init()`.
- Calls `jffs2_build_filesystem()`.
- Computes trigger levels with `jffs2_calc_trigger_levels()`.

On build failure it frees inode caches, raw node refs, summary state, and eraseblock storage.

## Filesystem Build Passes

`jffs2_build_filesystem()` runs the mount reconstruction sequence:
- Sets `JFFS2_SB_FLAG_SCANNING` and calls `jffs2_scan_medium()` to build inode caches and physical node references.
- Sets `JFFS2_SB_FLAG_BUILDING`.
- Pass 1: for every inode with scanned dirents, `jffs2_build_inode_pass1()` increments child inode link counts and detects possible directory hardlinks.
- Pass 2: removes inodes with zero link count using `jffs2_build_remove_unlinked_inode()`.
- Pass 2a: recursively processes children that became unlinked through dead directory removal.
- Final pass: frees temporary dirent lists and, for directories, records parent inode number in `pino_nlink`.
- Builds the xattr subsystem through `jffs2_build_xattr_subsystem()`.
- Clears build flags, rotates lists for wear leveling, and returns success.

## Directory and Link Reconstruction

`jffs2_build_inode_pass1()` walks temporary scanned dirents:
- Ignores deletion dirents with `ino == 0`.
- Resolves child inode caches.
- Marks raw dirent nodes obsolete if the referenced child inode does not exist.
- Reuses the dirent `raw/ic` union to store child inode cache pointers after validation.
- Increments `pino_nlink`.
- Marks directories and detects possible hard-linked directories.

The final cleanup pass converts directory child `pino_nlink` from temporary link count into parent inode number, warning if directory hardlinks remain.

## Unlinked Inode Removal

`jffs2_build_remove_unlinked_inode()`:
- Marks every raw node for an unlinked inode obsolete.
- If the inode was a directory, walks its child dirents and decrements each child’s temporary link count.
- Adds children that become unlinked to a `dead_fds` work list for later cleanup.
- Leaves inode cache deletion to erase code after physical nodes are fully gone.

This avoids recursion while cleaning dead directory subtrees discovered during mount.

## GC Trigger Levels

`jffs2_calc_trigger_levels()` computes reservation thresholds:
- Blocks needed to permit deletion.
- Blocks needed to permit writes.
- Background GC wake threshold.
- GC merge threshold.
- Bad-block GC threshold.
- Dirty-space threshold below which GC is not worth attempting.
- Very-dirty-block trigger threshold, larger when obsolete nodes can be marked on flash.

These fields drive space reservation and background GC wake behavior elsewhere in JFFS2.

## Important Invariants

- During build, `pino_nlink` is first used as a link count and later as parent inode number for directories.
- Temporary `scan_dents` must be freed on both success and failure.
- Missing child inode references are treated as obsolete dirent nodes.
- Directory hardlinks are detected and reported because normal directory topology should be single-parent.
- Xattr subsystem build happens only after core inode/dirent reconstruction.
- Eraseblock arrays mirror the physical MTD eraseblock layout exactly.

## Research Notes

This file is mount-time reconstruction logic for a log-structured flash filesystem. Its correctness depends on carefully interpreting scanned historical nodes, deletion dirents, obsolete nodes, and link counts so the in-memory inode tree reflects the latest valid flash state.
