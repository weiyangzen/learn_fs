# File Research: sources/local-fs/e2fsprogs/e2fsck/pass1.c

## Purpose

`pass1.c` implements e2fsck pass 1: a sequential inode-table scan. Its job is to validate every inode, account for all inode-owned blocks, discover duplicate block claims, collect directory block lists for pass 2, and build the bitmaps/counters that later passes depend on.

The file-level comment lists the pass outputs: in-use inode map, directory map, regular-file map, bad-inode map, bad-block-inode map, imagic map, casefold map, found-block map, duplicate-block map, directory block list, EA inode refs, and encryption policy data.

## Main Entry Points

- `e2fsck_pass1(e2fsck_t ctx)`: orchestrates pass 1.
- `e2fsck_pass1_check_device_inode(...)`: validates char/block device, FIFO, and socket inode block fields.
- `e2fsck_pass1_check_symlink(...)`: validates symlink size, fast symlink contents, inline-data symlinks, and single-block or extent-backed symlinks.
- `e2fsck_setup_icount(...)`: creates inode reference-count structures, optionally backed by scratch tdb files.
- `e2fsck_clear_inode(...)`: clears an inode and updates pass-1 in-memory maps.
- `e2fsck_use_inode_shortcuts(...)`: installs/removes libext2fs callbacks that reuse the current stashed inode.
- `e2fsck_intercept_block_allocations(...)`: installs allocation callbacks so later block allocation updates pass-1 block maps.

## Core Control Flow

`e2fsck_pass1` initializes readahead, problem context, feature flags, and maximum direct/indirect file sizes. It allocates all major bitmaps, creates `inode_link_info`, initializes the directory block list, clears `s_last_orphan`, marks filesystem metadata blocks, converts the found-block bitmap to subcluster-aware form, and starts an inode scan.

For every inode, it handles scan errors and checksum failures, then validates or repairs:

- deleted inode `dtime` inconsistencies
- link-count bookkeeping
- casefold flags and casefold feature consistency
- EA inode flags and EA inode refcount tracking
- conflicting inline-data and extent flags
- inline-data feature and missing `system.data` xattr
- extent feature mismatch and unset extent flags
- special reserved inodes: bad-block inode, root, journal, quota inodes, orphan-file inode, resize inode, boot loader inode
- invalid mode, flags, Hurd fragment fields, high block/ACL fields, imagic flags
- large inode extra space and in-inode extended attributes
- "looks like a directory" recovery for corrupted modes
- encryption policy registration
- inode classification into directory, regular file, device, symlink, FIFO, socket, or bad inode

Block-heavy non-extent inodes with indirect blocks or external EA blocks are queued into `inodes_to_process` and sorted by indirect block / EA block locality before `check_blocks` runs. Other inodes are checked immediately.

## Block and Metadata Accounting

`check_blocks` is the main per-inode block accounting routine. It validates external EA blocks through `check_ext_attr`, handles inline-data directories through `check_blocks_inline_data`, extent-mapped files through `check_blocks_extents`, and legacy block maps through `ext2fs_block_iterate3` with `process_block`.

Important block logic:

- `mark_block_used` populates `block_found_map` and creates/populates `block_dup_map` on duplicate claims unless shared-block handling suppresses it.
- `mark_blocks_used` accounts for cluster-sized allocations.
- `process_block` validates block numbers, file/directory size bounds, metadata collisions, fragmentation, bigalloc cluster alignment, directory block list insertion, and illegal block cleanup.
- `process_bad_block` validates the bad-block inode and detects bad blocks overlapping superblocks, group descriptors, bitmaps, inode tables, or bad-block inode metadata.
- `scan_extent_node` recursively validates extent trees, detects bad starts, out-of-order ranges, logical collisions, out-of-bounds extents, directory holes, uninitialized directory blocks, metadata collisions, checksum failures, and extent-tree rebuild candidates.
- `handle_htree` validates indexed directory root metadata and htree depth/hash compatibility.

## Extended Attribute Handling

The file has substantial EA logic:

- `check_inode_extra_space` validates large-inode `i_extra_isize`, in-inode EA headers, and old negative timestamp encodings.
- `check_ea_in_inode` validates in-inode EA entries, value bounds, hash correctness, collision-free layout, and EA inode references.
- `check_large_ea_inode` verifies EA value inodes, EA inode flags, hashes, and quota contribution.
- `check_ext_attr` validates external EA blocks, EA block magic/version, checksums, entry names, values, hash values, EA inode references, reference counts, and quota accounting.
- `adjust_extattr_refcount` fixes EA block refcounts after all inodes have been scanned.

## Repair Side Effects

Pass 1 can write inodes, superblocks, group descriptors, EA blocks, and metadata relocation changes. It may set restart flags when metadata was relocated or when unsafe repairs require another pass. It reserves one block each for possible root and lost+found creation, handles filesystem bad blocks with `new_table_block`, and may invoke pass 1B via `e2fsck_pass1_dupblocks` if `block_dup_map` is populated.

## Integration with Later Passes

Pass 1 feeds pass 2 with `fs->dblist`, `inode_used_map`, `inode_dir_map`, `inode_reg_map`, `inode_bad_map`, encrypted file info, casefold maps, and directory/htree tracking. It feeds pass 3 with directory info and reserved repair blocks. Duplicate blocks are delegated to `pass1b.c`.

## Risk and Test Focus

High-risk behavior is concentrated in extent-tree mutation, external/in-inode EA validation, bigalloc cluster accounting, duplicate-block detection, and metadata-block relocation. Regression tests should cover inline-data directories, encrypted/casefolded directories, EA inodes, shared-block unsharing, invalid htree roots, bad block metadata collisions, and corrupted extent trees that require restart.
