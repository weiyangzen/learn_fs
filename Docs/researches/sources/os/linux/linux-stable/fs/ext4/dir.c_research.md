# File Research: sources/os/linux/linux-stable/fs/ext4/dir.c

## Purpose

Implements ext4 directory reading, directory entry validation, htree indexed directory iteration, directory seek behavior, and directory file operations.

## Main Responsibilities

- Detects htree-indexed directories.
- Validates ext4 directory entries.
- Implements linear and htree-backed `readdir`.
- Handles encrypted directory names during emit.
- Handles inline-data directories.
- Converts htree hash values to/from file positions.
- Stores htree results in a red-black tree ordered by hash.
- Provides ext4 directory file operations.

## Key Operations

- `is_dx_dir()` detects directories using, or eligible for, htree indexing based on `dir_index`, inode index flag, one-block size, or inline data.
- `is_fake_dir_entry()` identifies dot entries and checksum tail entries for validation sizing.
- `__ext4_check_dir_entry()` validates record length, alignment, name length, block bounds, checksum-tail spacing, inode bounds, and invalid final `.` placement. It reports errors through file or inode error paths.
- `ext4_readdir()` prepares fscrypt, tries htree iteration first, falls back for bad non-checksummed htree directories, handles inline data, reads mapped directory blocks, verifies directory block checksums, rescans when inode version changes, validates entries, decrypts names when needed, and emits entries with `dir_emit()`.
- `hash2pos()`, `pos2maj_hash()`, `pos2min_hash()`, and `ext4_get_htree_eof()` encode htree hash positions for 32-bit and 64-bit APIs.
- `ext4_dir_llseek()` uses hash-position seeking for htree directories and normal ext4 llseek otherwise.
- `struct fname` stores htree directory entries by hash/minor hash with a collision chain.
- `free_rb_tree_fname()` frees cached htree entries.
- `ext4_htree_init_dir_info()` initializes per-open directory htree state.
- `ext4_htree_free_dir_info()` frees per-open state.
- `ext4_htree_store_dirent()` inserts decoded htree entries into the rb tree.
- `call_filldir()` emits entries from a hash collision chain and remembers the next entry if the caller’s buffer fills.
- `ext4_dx_readdir()` fills and drains the htree rb tree, restarts when `f_pos` changes or directory version changes, and sets htree EOF.
- `ext4_check_all_de()` validates every dirent in a buffer.
- `ext4_dir_open()` allocates `dir_private_info`.
- `ext4_release_dir()` frees per-open directory state.

## File Operations

`ext4_dir_operations` provides:

- `.open = ext4_dir_open`
- `.llseek = ext4_dir_llseek`
- `.read = generic_read_dir`
- `.iterate_shared = ext4_readdir`
- `.unlocked_ioctl = ext4_ioctl`
- optional `.compat_ioctl`
- `.fsync = ext4_sync_file`
- `.release = ext4_release_dir`
- `.setlease = generic_setlease`

## Dependencies

- Includes VFS, buffer heads, file locking, slab, inode versioning, unicode, `ext4.h`, and `xattr.h`.
- Uses fscrypt, ext4 htree fill, inline directory handling, block mapping, block checksums, directory checksums, inode versioning, and dtype conversion.

## Research Notes

This file is a high-value correctness surface because directory parsing is exposed to untrusted disk data. Validation is layered: block checksum first, then per-entry record validation, then inode bounds. Htree iteration decouples disk order from userspace order by caching entries in hash order.
