# File Research: sources/os/linux/linux/fs/nilfs2/namei.c

`namei.c` implements NILFS VFS pathname operations and NFS export file-handle support. The implementation follows ext2/minix-style directory manipulation, but every mutating namespace operation is wrapped in NILFS transactions so changes become part of log construction.

Core operations include lookup, create, mknod, symlink, hard link, mkdir, unlink, rmdir, and rename. Creation paths allocate a NILFS inode, install inode/file/address-space operations, mark it dirty, then link it into the directory with `nilfs_add_link()`. `nilfs_add_nondir()` centralizes the success path (`d_instantiate_new`) and failure cleanup for non-directory objects.

Removal and rename use directory-entry helpers from `dir.c`: `nilfs_find_entry`, `nilfs_delete_entry`, `nilfs_set_link`, `nilfs_dotdot`, and `nilfs_empty_dir`. Link counts and ctime are adjusted explicitly. `nilfs_rename()` supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`. Directory renames update `..` when crossing parent directories.

Symlinks are stored through `page_symlink()` with `nilfs_aops`; names longer than one filesystem block are rejected. Lookup rejects names longer than `NILFS_NAME_LEN`, resolves inode numbers via `nilfs_inode_by_name()`, and treats `-ESTALE` from `nilfs_iget()` as on-disk inconsistency.

Export support encodes checkpoint number, inode number, generation, and optional parent identity in `struct nilfs_fid`. `nilfs_get_dentry()` resolves handles through `nilfs_lookup_root()` and `nilfs_iget()`, which makes exported snapshots/checkpoints addressable by checkpoint number.
