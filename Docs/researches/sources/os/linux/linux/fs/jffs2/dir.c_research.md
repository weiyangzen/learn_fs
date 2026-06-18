# File Research: sources/os/linux/linux/fs/jffs2/dir.c

This file implements JFFS2 directory file and inode operations: lookup, readdir, create, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

`jffs2_lookup()` hashes the target name with `full_name_hash()`, walks the directory’s sorted `full_dirent` list under `dir_f->sem`, chooses the newest matching dirent version, and returns `d_splice_alias()` for the resolved inode if `ino` is nonzero.

`jffs2_readdir()` emits `.` and `..`, then iterates `f->dents` under `f->sem`, using `ctx->pos` as a linear cookie and skipping deletion dirents (`ino == 0`).

Creation-style operations allocate raw inode/dirent records, reserve flash space, create a new inode with `jffs2_new_inode()`, write inode metadata or data nodes, initialize security and ACLs, then write and link a parent dirent. `jffs2_create()` delegates most work to `jffs2_do_create()`. `jffs2_symlink()`, `jffs2_mkdir()`, and `jffs2_mknod()` explicitly write their initial metadata nodes before the parent dirent. Symlinks cache the target in `f->target` and `inode->i_link`; directories set initial nlink 2 and store parent inode in `pino_nlink`; device nodes encode `dev_t` using `jffs2_encode_dev()`.

`jffs2_unlink()` writes a deletion dirent through `jffs2_do_unlink()`, updates the victim nlink from the inocache, and updates parent times. `jffs2_rmdir()` first checks that all child dirents are deletion entries, then unlinks and drops directory link counts. `jffs2_link()` writes a new dirent to the old inode and increments `pino_nlink`.

`jffs2_rename()` only accepts `RENAME_NOREPLACE`. It implements rename as link-new then unlink-old, with explicit victim handling and directory nlink updates. If the unlink-old step fails after link-new succeeds, it logs that a hard link remains and invalidates the new dentry.

Key dependencies: raw node writers in `write.c`, allocation and node-list helpers, `fs.c` inode creation/read paths, ACL/xattr/security hooks, CRC32, and VFS dentry/inode APIs.

Important behavior: rename is not atomically represented by a single on-flash node, and the code explicitly documents the hard-link fallback risk on partial failure.
