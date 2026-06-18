# File Research: sources/os/linux/linux-stable/fs/udf/namei.c

## Summary
Implements UDF directory name lookup, create/link/unlink/mkdir/rmdir/mknod/symlink/rename/tmpfile operations, directory entry insertion/deletion, LVID file/dir counters, and exportfs file handles.

## Main Responsibilities
- Searches directory file identifier descriptors using `udf_fileident_iter`.
- Converts on-disk CS0 names to VFS names and honors `unhide`/`undelete` mount flags.
- Adds directory entries, reusing deleted FIDs when sizes match or appending new entries.
- Expands directories stored as `AD_IN_ICB` into external extents when an inline directory no longer fits.
- Creates regular files, special files, directories, symlinks, temporary files, and hard links.
- Deletes and renames directory entries while updating link counts, timestamps, and UDF LVID counters.
- Implements NFS/exportfs encoding and decoding using UDF logical block address plus generation.

## Important Behavior
UDF symlinks are stored as ECMA path components. `udf_symlink()` serializes absolute roots, `.`/`..`, and normal components into pathComponent records, using UDF filename conversion for normal names.

`udf_rename()` verifies that old and new directory entries match their VFS inodes, handles non-empty directory replacement rejection, updates `..` when moving a directory across parents, and adjusts link counts and LVID counters.

## Risks
Directory entry allocation can move data, so rename deliberately refinds the old entry after adding/reusing the target entry. Inline-directory expansion must rewrite FID tag locations after copying data into the new block.
