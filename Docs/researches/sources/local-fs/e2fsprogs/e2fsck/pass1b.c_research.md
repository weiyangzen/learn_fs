# File Research: sources/local-fs/e2fsprogs/e2fsck/pass1b.c

## Purpose

`pass1b.c` implements e2fsck passes 1B, 1C, and 1D. These run only when pass 1 found blocks claimed by more than one inode.

The three subpasses are:

- Pass 1B: rescan inode blocks and build complete duplicate block/cluster ownership records.
- Pass 1C: scan directories to find parent directories for duplicate-owning inodes so user prompts can show path context.
- Pass 1D: reconcile conflicts by cloning shared blocks or deleting files.

## Main Entry Point

- `e2fsck_pass1_dupblocks(e2fsck_t ctx, char *block_buf)`: allocates `inode_dup_map`, initializes duplicate dictionaries, runs `pass1b`, `pass1c`, and `pass1d`, clears the shared-block feature if unsharing succeeded, and frees all temporary duplicate-tracking state.

## Data Structures

Duplicate ownership is stored in two dictionaries:

- `clstr_dict`: keyed by cluster number; values are `struct dup_cluster`, containing `num_bad` and an inode list.
- `ino_dict`: keyed by inode number; values are `struct dup_inode`, containing parent dir, duplicate block count, copied inode, and duplicate cluster list.

Helper list structures:

- `struct cluster_el`: linked list of clusters per inode.
- `struct inode_el`: linked list of inodes per duplicate cluster.
- `inode_dup_map`: bitmap of inodes containing duplicate blocks.

The code tracks clusters, not only blocks, to handle bigalloc and logical-cluster-to-physical-cluster anomalies.

## Pass 1B Flow

`pass1b` opens a full inode scan, skips unused inodes except the bad-block inode, and iterates valid block mappings with `process_pass1b_block`. It also checks external EA blocks through the synthetic `BLOCK_COUNT_EXTATTR`.

`process_pass1b_block` detects whether a block is in `ctx->block_dup_map`. For duplicate blocks it:

- emits duplicate ranges for reporting
- marks the inode in `inode_dup_map`
- records duplicate ownership when crossing logical cluster boundaries, physical cluster changes, or negative block counts for metadata blocks
- updates current logical and physical cluster state

## Pass 1C Flow

`pass1c` iterates all directory entries from `fs->dblist`. `search_dirent_proc` checks whether each entry points to an inode in `inode_dup_map`. If so, it records the containing directory in that inode's `dup_inode` record. Root is handled specially in `add_dupe`.

## Pass 1D Flow

`pass1d` reads the real filesystem bitmaps, reports duplicate inode counts, then for every duplicate inode:

- builds a unique list of other inodes sharing its clusters
- detects whether shared clusters overlap filesystem metadata through `check_if_fs_cluster`
- reports the conflicting inode and shared inode list
- skips files whose duplicate state is already effectively handled
- tries `clone_file` when unsharing is requested or the user accepts clone repair
- otherwise optionally calls `delete_file`
- marks the filesystem invalid if the conflict remains unresolved

## Clone and Delete Behavior

`clone_file` uses `clone_file_block` as a block iterator callback. For duplicate blocks, it tries `ext2fs_map_cluster_block` first, then allocates a new block from `ctx->block_found_map` if needed. It copies block contents, updates directory block list entries for directory inodes, marks new blocks in both pass and filesystem bitmaps, and returns `BLOCK_CHANGED` unless running a no-write unshare check.

The `deferred_dec_badcount` mechanism delays duplicate-count decrementing until the next iterator callback or the successful end of iteration, preventing badcount underflow if remapping fails after a new block is chosen.

External EA block cloning is handled after rereading the inode. If an EA block is cloned, all other duplicate-inode records that pointed to the old EA block are updated to point at the new EA block.

`delete_file` iterates blocks with `delete_file_block`, decrements duplicate counts, frees non-duplicate blocks from allocation stats, updates inode bitmaps, quota accounting, rereads the inode, clears it through `e2fsck_clear_inode`, and adjusts EA refcounts when needed.

## Integration Points

This file depends directly on pass-1 outputs: `block_dup_map`, `block_found_map`, `block_metadata_map`, `inode_used_map`, `inode_dir_map`, `inode_reg_map`, `inode_bad_map`, and `fs->dblist`. It updates quota state, filesystem block maps, directory block list entries, and shared-block feature flags.

## Risk and Test Focus

High-risk behavior includes bigalloc cluster duplicate tracking, duplicate EA block cloning, metadata-overlap decisions, `E2F_OPT_UNSHARE_BLOCKS` no-write mode, and consistency between duplicate dictionaries and bitmap state. Tests should include shared reflink-like files, duplicate external xattr blocks, duplicate directory blocks, metadata block collisions, and failed block allocation during clone.
