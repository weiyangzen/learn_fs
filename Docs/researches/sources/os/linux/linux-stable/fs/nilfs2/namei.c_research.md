# File Research: sources/os/linux/linux-stable/fs/nilfs2/namei.c

`namei.c` implements NILFS pathname and namespace inode operations. It is derived from ext2/minix namei patterns but wraps all mutating operations in NILFS transactions so namespace updates become part of log construction.

Lookup validates `NILFS_NAME_LEN`, resolves directory entries through `nilfs_inode_by_name()`, loads target inodes with `nilfs_iget()`, treats stale deleted-inode references as filesystem errors, and returns aliases through `d_splice_alias()`. Creation paths (`create`, `mknod`, `symlink`, `mkdir`) allocate inodes with `nilfs_new_inode()`, install proper inode/file/address-space operations, mark inodes dirty, add directory links, and commit or abort the transaction.

Deletion and rename paths use directory helpers from `dir.c`: `nilfs_find_entry`, `nilfs_delete_entry`, `nilfs_dotdot`, `nilfs_set_link`, and `nilfs_empty_dir`. `nilfs_do_unlink()` validates that the directory entry inode matches the dentry inode, repairs zero-link anomalies with a warning, deletes the entry, and drops the target link. `rmdir` requires an empty directory and updates parent/child link counts. `rename` supports only `RENAME_NOREPLACE`, handles target replacement, cross-directory dotdot updates, directory link counts, ctime updates, and dirty marking of affected inodes/directories.

The file also implements export/NFS support. File handles encode checkpoint number, inode number, generation, and optional parent identity in `struct nilfs_fid`; `fh_to_dentry` and `fh_to_parent` resolve through `nilfs_lookup_root()` and `nilfs_iget()`. This checkpoint-aware handle format is important because NILFS snapshots expose historical roots.

Published operation tables are `nilfs_dir_inode_operations`, `nilfs_special_inode_operations`, `nilfs_symlink_inode_operations`, and `nilfs_export_ops`. The directory operations surface standard VFS entry points plus NILFS file attributes and fiemap hooks.
