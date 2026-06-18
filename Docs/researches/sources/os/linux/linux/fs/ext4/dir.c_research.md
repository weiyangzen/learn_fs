# File Research: sources/os/linux/linux/fs/ext4/dir.c

## Purpose
Implements ext4 directory file operations, directory entry validation, linear and htree readdir, htree seek-position mapping, encrypted-name emission, and per-open directory iteration state.

## Main Responsibilities
- `is_dx_dir()` detects htree-indexed or potentially indexed directories.
- `__ext4_check_dir_entry()` validates rec_len, alignment, name length, block bounds, checksum-tail placement, inode range, and invalid terminal `"."` entries.
- `ext4_readdir()` handles fscrypt preparation, htree fallback, inline directories, linear block mapping, readahead, checksum verification, i_version rescan safety, encrypted filename conversion, and `dir_emit()`.
- Hash/position helpers convert htree major/minor hashes to 32-bit or 64-bit directory offsets.
- `ext4_dir_llseek()` seeks by htree hash space for indexed directories and resets cached iteration state.
- `ext4_htree_store_dirent()` stores htree entries in a red-black tree ordered by hash/minor hash, with linked-list collision chains.
- `ext4_dx_readdir()` fills and drains the htree-sorted rb tree, preserving state across calls and handling hash-collision leftovers.
- `ext4_check_all_de()` validates all entries in a directory buffer.
- `ext4_dir_open()` allocates per-file private iteration state; `ext4_release_dir()` frees it.
- Exports `ext4_dir_operations`.

## Integration Points
Uses ext4 block mapping/bread, htree fill logic from other ext4 directory code, fscrypt, casefold hash metadata, metadata checksums, file readahead, inode i_version, VFS dir context, ioctl/fsync hooks, and generic lease handling.

## Risks and Edge Cases
Directory corruption handling skips bad blocks/entries and reports ext4 errors. Htree offsets are hash-derived, so 32-bit compatibility affects seek cookies. Encrypted and casefolded directories require hash/minor-hash preservation for stable userspace names. The per-open rb tree must be invalidated when directory i_version changes.
