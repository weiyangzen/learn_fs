# File Research: sources/os/linux/linux/fs/f2fs/namei.c

Implements F2FS VFS name/inode operations: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, encrypted symlink lookup, and inode operation tables.

Key responsibilities:
- Maintains hot/cold extension lists and applies file-temperature hints.
- Applies compression inheritance and extension-based compression policy to new inodes.
- Allocates and initializes new inodes with NIDs, fscrypt setup, quota setup, extra attributes, inline xattrs, inline dentries, inline data, project quota inheritance, inode flags, timestamps, generation, and extent tree setup.
- Implements all directory entry mutations under F2FS operation locks.
- Handles orphan inode accounting for unlink, tmpfile, and rename overwrite cases.
- Supports casefolding, fscrypt lookup, encrypted symlink targets, and ACL/xattr operation registration.

Important functions:
- `is_extension_exist()`: shared extension matcher for hot/cold and compression extension rules, including optional temporary suffix handling.
- `f2fs_update_extension_list()`: adds/removes hot or cold extensions inside the raw superblock extension list.
- `set_compress_new_inode()`: applies compression or no-compression behavior based on mount options, extension lists, and parent directory flags.
- `set_file_temperature()`: marks files hot or cold based on configured extensions.
- `f2fs_new_inode()`: central inode creation path; allocates a NID, initializes VFS and F2FS inode metadata, prepares encryption/quota state, and sets inline/compression flags.
- `f2fs_create()`, `f2fs_link()`, `f2fs_unlink()`, `f2fs_symlink()`, `f2fs_mkdir()`, `f2fs_rmdir()`, `f2fs_mknod()`: standard VFS operations mapped to F2FS metadata updates.
- `__f2fs_tmpfile()`: common tmpfile and whiteout creation path.
- `f2fs_rename()` and `f2fs_cross_rename()`: handle normal rename, overwrite, whiteout, and exchange rename cases.
- `f2fs_rename2()`: validates flags, performs fscrypt rename preparation, and dispatches to normal or exchange rename.
- `f2fs_encrypted_get_link()` / `f2fs_encrypted_symlink_getattr()`: encrypted symlink support.

Operation tables:
- `f2fs_dir_inode_operations`: directory operations, ACLs, xattrs, fiemap, fileattr get/set.
- `f2fs_symlink_inode_operations`: plain symlink operations.
- `f2fs_encrypted_symlink_inode_operations`: encrypted symlink operations.
- `f2fs_special_inode_operations`: special-file operations.

Consistency and recovery behavior:
- Creation/link/rename paths check checkpoint errors and checkpoint readiness before metadata mutation.
- Directory sync parents trigger `f2fs_sync_fs()`.
- Lookup and unlink detect zero-link or malformed directory inodes, mark `SBI_NEED_FSCK`, and return corruption errors.
- Rename updates parent inode numbers for moved directories so fsck can validate parent links.
- Strict fsync mode tracks transformed directory inodes with `TRANS_DIR_INO`.

Dependencies:
- Uses directory helpers from F2FS core, node allocation from `node.h`, segment/orphan/checkpoint handling from `segment.h`, xattr/ACL helpers, quota, fscrypt, casefolding, and F2FS tracepoints.
