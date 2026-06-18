# File Research: sources/os/linux/linux-stable/fs/9p/fid.c
- Purpose: Manages 9P FID lookup, cloning, attachment to dentries/inodes, and path walking.
- Main functions: `v9fs_fid_add`, `v9fs_fid_find_inode`, `v9fs_open_fid_add`, `build_path_from_dentry`, `v9fs_fid_lookup`.
- Dentry model: Stores FIDs in `d_fsdata` hlist entries, releases them from dentry operations, and reuses/duplicates them for parent/child walks.
- Inode model: Tracks open FIDs in `v9fs_inode->writeback_fid` and open fid lists so cached writeback and netfs operations can find suitable readable/writeable handles.
- Lookup flow: Builds path components up to a usable ancestor/root FID, performs 9P walk, and handles clone/retry logic.
- Risks: Correct fid reference counting is critical; lookup must balance dentry aliasing, disconnected dentries, open-file writeback requirements, and uid-specific access.
