# File Research: sources/os/linux/linux/fs/ntfs3/dir.c

Read coverage: complete file, 679 lines.

This file implements ntfs3 directory name conversion, lookup helper behavior, directory iteration, emptiness/count checks, and directory file operations.

Key functions:
- `ntfs_utf16_to_nls()` converts little-endian UTF-16 NTFS names to the mount NLS encoding or UTF-8, replacing unconvertible characters with `_` and logging the first conversion failure.
- `_utf8s_to_utf16s()` and `put_utf16()` convert UTF-8 to UTF-16 with explicit output-limit handling and surrogate-pair support.
- `ntfs_nls_to_utf16()` converts VFS byte names to UTF-16 for NTFS creation/lookup, using mount NLS or UTF-8.
- `dir_search_u()` searches a directory index for a UTF-16 name and returns an inode from the found reference.
- `ntfs_dir_emit()` filters directory entries, converts names, determines `d_type`, skips DOS aliases, root/self/meta/hidden entries as configured, and emits to `dir_context`.
- `ntfs_read_hdr()` walks one NTFS index header and emits entries while validating entry sizes and key sizes.
- `ntfs_readdir()` implements `iterate_shared`, emits dot entries, loads subrecords if needed, enumerates root index entries then index allocation buffers, and handles directories modified during readdir by rewinding to a stable internal position.
- `ntfs_dir_count()` counts child directories/files and supports emptiness checks.
- `dir_is_empty()` wraps `ntfs_dir_count()`.
- `ntfs_dir_operations` wires directory file operations: llseek, generic directory read, iterate, fsync, open, ioctl, compat ioctl, and lease handling.

Integration:
- Depends on ntfs3 index lookup/enumeration, MFT inode loading, NLS conversion, directory index metadata, and file operation helpers.
- Directory enumeration uses `indx_find`, `indx_get_root`, `indx_used_bit`, `indx_read_ra`, and `ntfs_iget5()`.

Risks:
- Directory parsing must validate index entry bounds carefully to avoid corrupt-directory walks.
- `ntfs_readdir()` intentionally uses non-sorted enumeration to avoid loops in corrupted name trees.
- Name conversion can truncate output when buffers are too small; current emit buffer is `PATH_MAX` and guarded by static assertions.
- `d_type` is partly inferred from duplicated directory information and may require opening the inode for more accurate extended-data cases.
