# File Research: sources/os/linux/linux-stable/fs/9p/Makefile
- Purpose: Builds the 9P filesystem module/object set.
- Main object: `9p.o` is built when `CONFIG_9P_FS` is enabled.
- Core objects: Includes session/superblock/VFS/inode/dentry/dir/file/fid/address-space/xattr support.
- Conditional objects: Adds `cache.o` under `CONFIG_9P_FSCACHE` and `acl.o` under `CONFIG_9P_FS_POSIX_ACL`.
- Integration: Encodes the module boundary for the whole `fs/9p` subtree.
