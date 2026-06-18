# File Research: sources/os/linux/linux-stable/fs/9p/fid.h
- Purpose: Declares FID lookup helpers and small inline wrappers.
- Main APIs: `v9fs_fid_find_inode`, `v9fs_fid_lookup`, `v9fs_parent_fid`, `clone_fid`, `v9fs_fid_clone`, `v9fs_fid_add_modes`.
- Integration: Used by nearly every VFS operation to obtain a protocol handle before issuing 9P requests.
- Behavior: `v9fs_fid_add_modes` annotates a FID with open mode/access/caching information derived from mount flags and file flags.
- Research notes: This header is the bridge between VFS objects and 9P client state.
