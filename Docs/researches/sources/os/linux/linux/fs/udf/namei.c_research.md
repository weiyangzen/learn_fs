# File Research: sources/os/linux/linux/fs/udf/namei.c

Purpose: VFS namespace operations for UDF directories.

Key behavior:
- `udf_fiiter_find_entry()` scans directory file identifier descriptors using `udf_fileident_iter`, honoring `undelete` and `unhide` mount flags, decoding CS0 filenames, and special-casing `..`.
- `udf_lookup()` resolves a dentry to an inode through the FID ICB location.
- `udf_expand_dir_adinicb()` converts an inline AD-in-ICB directory into external allocation descriptors when it outgrows inode storage, copies directory bytes to a new block, and fixes moved FID tag locations.
- `udf_fiiter_add_entry()` reuses deleted entries of exact size or appends a new FID, growing directories and updating extent length.
- `udf_create()`, `udf_tmpfile()`, `udf_mknod()`, `udf_mkdir()`, `udf_unlink()`, `udf_rmdir()`, `udf_link()`, and `udf_rename()` implement normal VFS operations.
- `udf_symlink()` encodes symlink text as UDF `pathComponent` records, using component types for root, parent, current directory, and named components.
- NFS export support is provided by `udf_encode_fh()`, `udf_fh_to_dentry()`, `udf_fh_to_parent()`, and `udf_get_parent()`.

Integration:
- Uses `udf_fiiter_*` from directory handling, `udf_new_inode()`, `udf_iget()`, UDF filename conversion, block allocation, extent helpers, and LVID counters.
- Exports `udf_dir_inode_operations` and `udf_export_ops`.

Risks and invariants:
- Directory entry mutations verify that FID target physical block matches the inode before unlink/rmdir/rename.
- Link/file counters in the Logical Volume Integrity Descriptor are adjusted for create/link/unlink/mkdir/rmdir/rename replacement.
- Rename only accepts `RENAME_NOREPLACE`; unsupported flags return `-EINVAL`.
- Directory renames across parents update the child `..` entry and carefully adjust parent link counts.
