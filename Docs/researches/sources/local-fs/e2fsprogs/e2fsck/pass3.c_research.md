# File Research: sources/local-fs/e2fsprogs/e2fsck/pass3.c

## Purpose

`pass3.c` implements e2fsck pass 3: directory connectivity checking. It ensures the root directory exists, verifies every directory is connected to the root through parent pointers gathered in pass 2, breaks directory loops, reconnects disconnected directories/files to `/lost+found`, fixes bad `..` entries, and runs deferred directory rehashing.

## Main Entry Points

- `e2fsck_pass3(e2fsck_t ctx)`: orchestrates pass 3.
- `e2fsck_get_lost_and_found(e2fsck_t ctx, int fix)`: finds or creates `/lost+found`.
- `e2fsck_reconnect_file(e2fsck_t ctx, ext2_ino_t ino)`: links an inode into `/lost+found` as `#<ino>`.
- `e2fsck_adjust_inode_count(e2fsck_t ctx, ext2_ino_t ino, int adj)`: updates on-disk and in-memory link counts.
- `e2fsck_expand_directory(...)`: expands a directory, mainly used when `/lost+found` has no room.

## Top-Level Flow

`e2fsck_pass3` allocates `inode_done_map`, calls `check_root`, marks root as done, iterates every directory info record, and calls `check_directory` for active directory inodes. After connectivity checks, it forces `/lost+found` creation in writable mode and calls `e2fsck_rehash_directories`.

On exit it frees the dirinfo cache, loop-detection bitmap, done bitmap, and releases any pass-1 reserved repair blocks that were not consumed.

## Root Repair

`check_root` verifies inode 2 exists and is a directory. If missing and the user accepts repair, it:

- reads bitmaps
- uses `ctx->root_repair_block` if reserved, otherwise allocates a free block
- creates a new root inode with mode `040755`, size one block, link count 2, timestamps, and block pointer
- writes the inode before writing the directory block because metadata checksums require this order
- writes a new directory block containing `.` and `..`
- updates dirinfo, inode counts, inode bitmaps, filesystem inode map, and quota accounting

If root exists but is not a directory, pass 3 aborts because pass 1 did not clear it.

## Directory Connectivity

`check_directory` walks parent pointers from a directory until it reaches an inode already marked done. To avoid paying bitmap-clearing costs on normal filesystems, it first walks without loop detection and only enables `inode_loop_detect` if the chain depth exceeds 2048.

If a directory has no parent or a loop is detected, it prompts to reconnect the directory to `/lost+found`. On successful reconnect, it calls `fix_dotdot` so the directory's `..` points at `/lost+found`.

After the connectivity walk, it compares the recorded `..` inode against the recorded parent. If they differ, it prompts and fixes `..`.

## Lost+Found Handling

`e2fsck_get_lost_and_found` first looks up `lost+found` in the root directory. If present, it rejects inline-data or encrypted lost+found directories when repair is requested, verifies it is a directory, and otherwise unlinks unusable entries. If missing or unusable, it creates a new directory:

- allocates a block, using `ctx->lnf_repair_block` if available
- allocates an inode under root
- writes the inode before its directory block
- links it into root as `lost+found`
- adds dirinfo, adjusts root link count, sets inode counts, caches `ctx->lost_and_found`, and updates quota

If there is no space and the user accepts the no-space recovery prompt, it can set `lost_and_found` to root as a fallback but returns failure for normal creation.

## Reconnection and Parent Fixes

`e2fsck_reconnect_file` ensures `/lost+found` exists, links the inode as `#<ino>`, expands `/lost+found` if needed, and increments the inode's link count.

`fix_dotdot` iterates a directory looking for `..`. `fix_dotdot_proc` decrements the old parent's link count, increments the new parent's link count, rewrites the dirent inode and file type, and records the new dotdot in dirinfo. If the directory is scheduled for rehash, checksum errors are temporarily ignored during iteration.

## Directory Expansion

`e2fsck_expand_directory` appends blocks to a directory using `BLOCK_FLAG_APPEND`. `expand_dir_proc` fills holes with new blocks, preferring cluster-contiguous allocation when possible, initializes new directory blocks, marks pass and filesystem allocation state, and updates inode size, block count, and quota.

## Integration Points

Pass 3 consumes `inode_dir_map`, `inode_used_map`, dirinfo parent/dotdot records, `inode_count`, `inode_link_info`, `block_found_map`, and reserved repair blocks from pass 1. It depends on pass 2 having populated parent pointers. It also triggers deferred rehashing from pass 1/pass 2.

## Risk and Test Focus

Key edge cases are missing root creation, unusable `/lost+found`, encrypted or inline-data lost+found entries, directory loops deeper than 2048, bad `..` entries, link-count adjustments during reparenting, expanding lost+found under low-space conditions, and metadata-checksum ordering when writing newly created directories.
