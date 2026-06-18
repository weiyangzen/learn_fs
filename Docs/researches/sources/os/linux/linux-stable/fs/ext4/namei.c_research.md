# File Research: sources/os/linux/linux-stable/fs/ext4/namei.c

## Summary
Implements ext4 directory and name operations: lookup, htree indexed-directory traversal, directory entry checksums, create/link/unlink/mkdir/rmdir/symlink/mknod/tmpfile, rename/exchange/whiteout, and inode operation tables for directories and special files.

## Main Responsibilities
- Read, validate, checksum, and dirty ext4 directory blocks and htree index blocks.
- Maintain htree directory indexes, including lookup, readdir tree fill, leaf splitting, index splitting, and conversion from linear to indexed directories.
- Support encrypted and casefolded filename lookup, including hash-in-dirent behavior.
- Add, delete, and update directory entries with journaling.
- Implement VFS inode operations for all directory namespace mutations.
- Maintain directory link counts, `.`/`..` entries, ctime/mtime, inode versions, orphan tracking, and fast-commit tracking.
- Handle inline-directory fallbacks and transitions.

## Important Structures
- `struct fake_dirent`, `struct dx_root`, `struct dx_node`, `struct dx_entry`, `struct dx_frame`: on-disk and in-memory htree directory index layout.
- `struct dx_map_entry`: temporary hash/offset/size map used when splitting directory leaf blocks.
- `struct dx_tail`: checksum tail for htree blocks.
- `struct ext4_renament`: rename helper state for a source or destination directory entry, including its dentry, inode, buffer, dirent, inline state, and optional parent `..` entry.

## Directory Block and Checksum Handling
- `__ext4_read_dirblock()` enforces bounds, reads directory blocks, distinguishes index blocks from leaf blocks, rejects directory holes in required htree paths, and verifies metadata checksums when enabled.
- `ext4_initialize_dirent_tail()` initializes checksum tail entries in directory leaf blocks.
- `ext4_dirblock_csum_verify()` and `ext4_dirblock_csum_set()` validate and update directory leaf checksums using the inode checksum seed.
- `ext4_dx_csum_verify()` and `ext4_dx_csum_set()` validate and update htree node checksums.
- `ext4_handle_dirty_dirblock()` and `ext4_handle_dirty_dx_node()` centralize checksum update before `ext4_handle_dirty_metadata()`.

## Htree Lookup and Readdir
- `dx_probe()` validates the htree root, hash version, hash-in-dirent compatibility, depth limits, entry counts, limits, and cycle-free traversal before returning a leaf path.
- `ext4_htree_next_block()` advances to the next leaf block for lookup continuation or hash-ordered readdir.
- `htree_dirblock_to_tree()` reads a leaf directory block into the readdir rb-tree, handling encrypted names, casefold/hash values, checksum limits, and corruption checks.
- `ext4_htree_fill_tree()` fills readdir state either from inline/linear directories or from indexed htree order.
- `ext4_dx_find_entry()` performs indexed lookup and follows continuation blocks when hash collisions require it.

## Entry Search, Insert, and Delete
- `ext4_match()` compares a dirent against a prepared ext4 filename, using fscrypt matching or Unicode casefold matching where applicable.
- `ext4_search_dir()` linearly scans one directory block and validates the matching entry before returning it.
- `__ext4_find_entry()` searches inline data, htree directories, then linear directory blocks with small readahead, falling back from bad htree indexes when allowed.
- `ext4_find_dest_de()` finds space for a new entry and detects duplicates.
- `ext4_insert_dentry()` writes inode number, type, name, and optional hash fields into a directory entry.
- `add_dirent_to_buf()` journals a directory block, inserts the entry, updates timestamps/version/dx flag, and dirties metadata.
- `ext4_generic_delete_entry()` deletes by merging with the previous record or clearing the first record.
- `ext4_delete_entry()` handles inline delete first, then journaled block delete and checksum update.

## Indexed Directory Growth
- `dx_make_map()` builds a compact map of live dirents and their hash values.
- `dx_sort_map()` sorts the map by hash.
- `do_split()` appends a new directory block, splits a full leaf approximately by occupancy/hash order, reinitializes checksums, inserts a new htree block pointer, and returns the target insertion point.
- `make_indexed_dir()` converts a one-block linear directory into an htree directory, moves normal dirents into a new leaf block, initializes the root index, and inserts the new entry.
- `ext4_dx_add_entry()` inserts into an indexed directory, splitting leaf blocks and htree index nodes as necessary, including adding a new htree level when supported.

## VFS Namespace Operations
- `ext4_lookup()` resolves a name to an inode, validates inode numbers, rejects self-linked parent entries, checks encryption context consistency, and avoids caching negative casefold dentries.
- `ext4_get_parent()` resolves `..` for export/NFS-style parent lookup.
- `ext4_create()`, `ext4_mknod()`, `ext4_tmpfile()`: allocate new inodes with journal handles and add or orphan them as appropriate.
- `ext4_init_dirblock()` and `ext4_init_new_dir()` initialize `.` and `..` entries, inline-directory data, checksum tails, and link counts.
- `ext4_mkdir()` creates directories, initializes contents, updates parent link counts, adds the entry, tracks fast commit, and handles orphan cleanup on failure.
- `ext4_empty_dir()` validates `.`/`..` and scans for live entries, including inline-directory support.
- `ext4_rmdir()` removes empty directories, deletes parent entry, clears child links, orphans the directory inode, updates counts, and invalidates casefold dentries.
- `__ext4_unlink()` and `ext4_unlink()` remove non-directory entries, drop link counts, add final-link inodes to the orphan list, and track fast commits.
- `ext4_symlink()` handles encrypted symlink preparation/encryption, fast symlink storage in inode data, block-backed symlink allocation, and failure orphaning.
- `__ext4_link()` and `ext4_link()` add hard links, enforce link/project constraints, update ctime/link count, and remove tmpfiles from orphan tracking.

## Rename Paths
- `ext4_rename_dir_prepare()` and `ext4_rename_dir_finish()` validate and update `..` for moved directories.
- `ext4_setent()` replaces a directory entry inode/type in-place.
- `ext4_resetent()` restores an entry after failed whiteout rename setup.
- `ext4_rename_delete()` deletes the old source entry, rereading if inline-to-block conversion may have invalidated stored pointers.
- `ext4_whiteout_for_rename()` creates a whiteout inode for `RENAME_WHITEOUT`.
- `ext4_rename()` implements normal rename, replacement, directory movement, whiteout rename, link-count transitions, orphaning of overwritten inodes, fast-commit tracking, and fast-commit exclusion for directory renames.
- `ext4_cross_rename()` implements `RENAME_EXCHANGE`, swapping dirents and updating `..` entries/link counts for directory/non-directory exchanges.
- `ext4_rename2()` validates flags, performs fscrypt rename checks, and dispatches to exchange or normal rename.

## Exported Operation Tables
- `ext4_dir_inode_operations`: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, setattr/getattr, xattrs, ACLs, fiemap, and fileattr operations.
- `ext4_special_inode_operations`: setattr/getattr, xattrs, ACLs.

## Synchronization and Journaling
Most namespace mutations run inside ext4 directory journal transactions and use buffer write access before modifying dirent blocks. VFS inode locking is assumed by callers for namespace operations. Directory checksums are updated before metadata dirtying. Link count and timestamp updates are journaled with inode dirtying. Fast commit is tracked for supported create/link/unlink/rename cases and explicitly disabled for directory rename and exchange cases not replayable by fast commit.

## Risks and Edge Cases
- Htree corruption can fall back to linear search only when metadata checksums do not force hard failure.
- Casefolded encrypted directories require careful hash and comparison ordering; a key arriving after name setup can invalidate hash-only assumptions.
- Inline directory conversion can move dirent storage during rename, requiring reread of source entries.
- Directory block checksum tails reduce usable dirent space and must be preserved during split/pack operations.
- Rename combines multiple mutable objects: old dir, new dir, source inode, target inode, optional whiteout inode, and possible `..` entries.
