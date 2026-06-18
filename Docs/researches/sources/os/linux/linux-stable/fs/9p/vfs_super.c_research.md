# File Research: sources/os/linux/linux-stable/fs/9p/vfs_super.c
- Purpose: Implements 9P superblock, mount, unmount, statfs, writeback, and fs_context behavior.
- Main functions: `v9fs_fill_super`, `v9fs_get_tree`, `v9fs_kill_super`, `v9fs_umount_begin`, `v9fs_statfs`, `v9fs_write_inode`, `v9fs_write_inode_dotl`, `v9fs_init_fs_context`.
- Mount flow: Initializes session, attaches root FID, instantiates root inode, selects operation tables based on protocol/cache/ACL/xattr options, and creates root dentry.
- Super operations: Provide statfs, drop_inode, write_inode, and show-options behavior.
- Fs context: Allocates mount context, wires parse/get_tree/free operations, and stores client/session options before mount.
- Integration: Registers `v9fs_fs_type`; coordinates with `v9fs.c` session setup and inode creation helpers.
- Risks: Mount failure paths must clunk FIDs and close sessions; dotl versus legacy write_inode behavior differs.
