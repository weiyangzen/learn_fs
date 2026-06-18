# File Research: sources/os/linux/linux-stable/fs/ntfs3/dir.c

This file implements ntfs3 directory name conversion, lookup by Unicode name, readdir iteration, directory entry emission, and directory emptiness/count checks.

Main responsibilities:
- Converts NTFS little-endian UTF-16 names to mounted NLS or UTF-8 output.
- Converts incoming NLS/UTF-8 names to UTF-16 for NTFS directory operations and symlink creation.
- Searches directory indexes for a Unicode name and returns the referenced inode.
- Emits directory entries while filtering DOS aliases, non-home entries, metadata files, hidden files, root self-reference, and malformed names.
- Iterates directory index root and allocation blocks in an unsorted physical/index order.
- Handles directories modified during readdir by restarting from a low position when the directory version changed after end-of-directory.
- Counts directories/files and checks whether a directory is empty.
- Defines `ntfs_dir_operations`.

Important functions:
- `ntfs_utf16_to_nls()` converts UTF-16 to UTF-8 when no NLS table is configured, or uses `uni2char()` with replacement and warning on conversion failure.
- `_utf8s_to_utf16s()` is a local UTF-8 to UTF-16 converter that detects output exhaustion before writing beyond the maximum.
- `ntfs_nls_to_utf16()` converts user names to UTF-16 in requested endian form.
- `dir_search_u()` calls `indx_find()` and then `ntfs_iget5()` for the matching directory entry reference.
- `ntfs_dir_emit()` validates and filters a directory entry, converts the file name, determines `d_type`, and may open the inode for more accurate type when extended duplicated info is present.
- `ntfs_read_hdr()` walks one `INDEX_HDR`, validates entry sizes and key sizes, updates `ctx->pos`, and calls the emitter.
- `ntfs_readdir()` emits dots, reads the index root, iterates used index allocation bits with readahead, and normalizes end/error positions.
- `ntfs_dir_count()` walks root and index blocks to count non-DOS directory and file entries.
- `dir_is_empty()` wraps `ntfs_dir_count()`.

Notable implementation details:
- Readdir intentionally uses non-sorted enumeration to avoid infinite loops if the directory name tree is corrupted.
- `ctx->pos` uses the index-root area first, then index allocation positions offset by `sbi->record_size`.
- `file->private_data` stores `ni->dir.version` to detect mutation during a directory stream.
- The comments explicitly discuss POSIX-unspecified readdir/unlink behavior and why ntfs3 attempts rmdir-like behavior for callers that remove while iterating.

Research notes:
- Directory presentation is strongly governed by mount options such as `showmeta` and `nohidden`.
- Dentry type from duplicated NTFS filename information is treated as potentially unreliable; the code optionally opens the inode for a better type in selected cases.
