# File Research: sources/os/linux/linux-stable/fs/exportfs/expfs.c

## Summary
Implements generic filesystem export support: encoding inodes/dentries into file handles and decoding file handles back into acceptable dentries for NFS, fanotify, and other exportfs consumers.

## Main Responsibilities
- Encodes inode- and dentry-based file handles.
- Provides a generic non-decodeable 64-bit inode/generation file identifier.
- Reconnects disconnected dentries to the dcache tree when subtree checks require connected paths.
- Finds child names by scanning parent directories when a filesystem lacks `get_name`.
- Validates decoded aliases against caller-provided acceptability rules.

## Key APIs
- `exportfs_encode_inode_fh()`.
- `exportfs_encode_fh()`.
- `exportfs_decode_fh_raw()`.
- `exportfs_decode_fh()`.

## Important Behavior
`exportfs_encode_inode_fh()` delegates to filesystem `export_operations->encode_fh()` when available, or emits an inode/generation FID for `EXPORT_FH_FID` users. User flag bits in returned fileid types are rejected.

Decode first asks the filesystem to turn a file handle into a dentry. Directory results may be reconnected to root through `reconnect_path()`. Non-directory results first try acceptable aliases, then decode and reconnect the parent, recover the child name, re-lookup under that parent, and re-run acceptability checks.

The default `get_name()` opens the parent directory and iterates entries until it finds the child inode number from `vfs_getattr_nosec()`.

## State and Synchronization
Dentry aliases are walked under `inode->i_lock` with temporary dentry references. Reconnect logic handles races where rename or delete reconnects or invalidates a target while exportfs is reconstructing a path.

## Risks
Reconnect behavior depends on filesystem `get_parent`, `fh_to_dentry`, and `fh_to_parent` correctness. Directory scans match by inode number, so filesystems with unstable inode identity or unusual directory semantics must provide robust export operations.
