# File Research: sources/local-fs/xfsprogs/db/rdump.c

Implements the `xfs_db` `rdump` command, which recovers files from an XFS filesystem image into a host directory.

Key responsibilities:
- Registers `rdump [-s] [paths...] dest_directory`.
- Walks the XFS namespace with `path_walk`, `listdir`, `libxfs_iget`, and a recursive path buffer.
- Recreates directories, regular files, symlinks, and special files in the destination tree.
- Copies file data by reading written extents directly from the data or realtime device.
- Preserves mode, owner, timestamps, XFS file attributes, project IDs, extent-size hints, CoW extent-size hints, xflags, and extended attributes where possible.
- Translates ondisk xattr namespaces to Linux xattr namespaces and skips parent-pointer attrs.
- Tracks degraded metadata restoration with `lost_mask` and reports aggregate warnings at the end.

Important behavior:
- `-s` enables strict mode: many metadata/data-copy failures become fatal instead of warnings.
- Dumping a single directory copies its children directly into the destination directory.
- Directory recursion ignores `.` and `..` and enforces `PATH_MAX`/`FILENAME_MAX`.
- Sparse/unwritten extents are skipped and final size is restored with `ftruncate`.
- Remote xattr values are fetched with `libxfs_attr_rmtval_get`.
- Symlink attributes/timestamps use `AT_SYMLINK_NOFOLLOW`.
- ACL xattrs copied to non-XFS targets are warned as likely untranslatable.

Dependencies:
- Relies on `libxfs` inode, bmap, symlink, attr, transaction, and buffer APIs.
- Uses `listxattr.h` xattr walking and `libfrog/file_attr.h` for path-based file attribute setting.
- Uses global `mp`, `iocur_top`, `exitcode`, `strict_errors`, and `lost_mask`.

Notable risks:
- Recovery is best-effort by default, so non-strict runs can silently produce incomplete data while only printing warnings.
- The xattr error check after `fsetxattr` compares `ret` to `EOPNOTSUPP` instead of checking `errno`; that can miss the intended lost-xattr classification.
- File contents are copied from raw written extents and do not reconstruct holes beyond final truncation.
- Host filesystem support and process privileges strongly affect fidelity of ownership, flags, ACLs, xattrs, devices, and symlink metadata.
