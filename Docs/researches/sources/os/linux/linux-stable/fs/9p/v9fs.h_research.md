# File Research: sources/os/linux/linux-stable/fs/9p/v9fs.h
- Purpose: Central private header for the 9P filesystem.
- Main types: `v9fs_session_info`, `v9fs_inode`, session flag enums, cache shortcut/bit enums.
- Session state: Holds the 9P client, mount options, cache mode, protocol version, uid/gid defaults, rename semaphore, fscache volume, and session list linkage.
- Inode state: Embeds `netfs_inode`, stores qid, cache validity flags, mutex, open fid list, and optional writeback fid.
- Main helpers: `V9FS_I`, `v9fs_inode_cookie`, `v9fs_session_cache`, `v9fs_inode2v9ses`, `v9fs_dentry2v9ses`, `v9fs_proto_dotu`, `v9fs_proto_dotl`.
- Integration: Declares VFS operation tables and inode-from-fid helpers used across superblock, inode, file, dentry, and address-space code.
- Risks: Session and inode structs encode coherency, protocol, and cache invariants shared across all 9P operations.
