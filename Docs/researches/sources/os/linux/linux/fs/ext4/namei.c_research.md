# File Research: sources/os/linux/linux/fs/ext4/namei.c

## Purpose
Implements ext4 directory name handling and VFS inode operations: lookup, create, link, unlink, symlink, mkdir, rmdir, tmpfile, mknod, rename, htree directory indexing, directory checksums, inline-directory fallback, casefold/encryption-aware matching, and directory entry mutation.

## Main Entry Points
- `ext4_dir_inode_operations` wires VFS operations to ext4 implementations.
- Lookup/search: `ext4_lookup()`, `ext4_get_parent()`, `ext4_find_entry()`, `__ext4_find_entry()`, `ext4_dx_find_entry()`, `ext4_search_dir()`.
- Creation/mutation: `ext4_create()`, `ext4_mknod()`, `ext4_tmpfile()`, `ext4_mkdir()`, `ext4_symlink()`, `ext4_link()`, `ext4_unlink()`, `ext4_rmdir()`, `ext4_rename2()`.
- Directory infrastructure: `ext4_init_dirblock()`, `ext4_init_new_dir()`, `ext4_handle_dirty_dirblock()`, `ext4_insert_dentry()`, `ext4_generic_delete_entry()`.

## Directory Block and Checksum Model
`__ext4_read_dirblock()` is the guarded directory read path. It verifies block bounds, detects index-vs-leaf expectations, rejects directory holes where illegal, and validates metadata checksums for htree index blocks and directory leaf blocks. Directory leaf checksums use the tail entry initialized by `ext4_initialize_dirent_tail()`. Htree node checksums use `dx_tail`, count/limit metadata, and inode checksum seeds.

## Htree Indexing
The file defines htree root/node/frame structures and helpers for hash/count/block access. `dx_probe()` validates the root hash version, casefold/encryption hash mode, tree depth, count/limit values, and cycle-free traversal before returning the matching leaf frame. `ext4_htree_next_block()` advances through continuation hash ranges. `htree_dirblock_to_tree()` and `ext4_htree_fill_tree()` support hash-ordered readdir by collecting dirents into the file-private tree.

Insertion into indexed directories uses `ext4_dx_add_entry()`. If a leaf is full, `do_split()` allocates a new block, builds and sorts a hash map, moves approximately half the entries, updates checksums, inserts a new dx index entry, and retries/proceeds. If the index block is full, the code either splits an internal node or increases htree depth, subject to maximum htree level and large-dir support.

## Lookup and Matching
`ext4_match()` handles normal, encrypted, and Unicode casefolded comparisons. For encrypted casefolded directories with hash-in-dirent support, it can use stored SipHash values to skip string comparison only when safe. Linear fallback scans directory blocks with bounded readahead and checksum verification; indexed lookup falls back to linear search on corrupt htree format when allowed.

## Directory Entry Mutations
`add_dirent_to_buf()` finds or uses available record space, journals the block, inserts the dentry, updates directory times, dx flags, inode version, and dirblock checksum. `ext4_generic_delete_entry()` deletes by merging with the previous record when possible or zeroing the first entry. Inline-data directories are tried before block-based paths and may force rereads after conversion.

## VFS Operations
File, special-file, tmpfile, and symlink creation allocate new inodes with journal handles and add directory entries; failure paths drop links and add new inodes to orphan tracking. `ext4_mkdir()` initializes `.` and `..`, updates parent link counts, and tracks fast commit creation. `ext4_empty_dir()` validates `.`/`..` then scans all entries. `__ext4_unlink()` removes a dentry, drops link count, adds zero-link inodes to the orphan list, and records fast commit unlink.

Rename is handled by `ext4_rename2()`, dispatching to `ext4_cross_rename()` for `RENAME_EXCHANGE` and `ext4_rename()` otherwise. Rename tracks old/new entries in `struct ext4_renament`, updates `..` for moved directories, supports whiteouts, handles overwritten targets, updates parent link counts, invalidates casefolded dentries where needed, and marks fast commits ineligible for directory/cross renames.

## Integration Points
Heavy dependencies include JBD2 journaling, ext4 inode allocation, extents/block mapping, inline data, fscrypt, Unicode casefolding, fsverity-adjacent name handling, quota initialization, fast commit tracking, VFS dentry APIs, and metadata checksum helpers.

## Invariants and Risks
Directory entry record lengths, block checksums, htree count/limit fields, link counts, and `.`/`..` parent pointers are critical invariants. Several comments explicitly note that after journaled on-disk mutation begins, rollback is not available, so validation is front-loaded. Rename has high risk due to stale dirent pointers after htree split or inline conversion, handled by forced reread/reset paths.

## Testing Signals
Cover encrypted/casefolded lookup, htree corruption fallback, checksum failures, inline-to-block conversion, htree leaf/internal splits, directory link-count overflow mode, fast commit tracking/ineligibility, whiteout rename, exchange rename, cross-directory directory rename, and orphan handling on failed create/unlink paths.
