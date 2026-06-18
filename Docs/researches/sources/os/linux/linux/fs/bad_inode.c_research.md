# File Research: sources/os/linux/linux/fs/bad_inode.c

## Summary
Provides VFS stub operations for inodes that could not be read or constructed correctly, causing further operations to fail with `-EIO`.

## Main Responsibilities
- Define bad inode file and inode operations.
- Convert an inode into a bad inode after I/O/read failure.
- Test whether an inode is bad.
- Abort construction of a newly allocated inode.

## Key APIs
- `make_bad_inode()`.
- `is_bad_inode()`.
- `iget_failed()`.

## Important Behavior
`make_bad_inode()` removes the inode from the inode hash, sets it to a regular-file mode with simple timestamps, installs `bad_inode_ops` and `bad_file_ops`, and clears xattr operation flags.

Almost all inode operations return `-EIO`; lookup and directory creation return error pointers. `iget_failed()` marks the inode bad, unlocks it as a new inode, and drops it with `iput()`.

## Risks
This is deliberately blunt failure containment. Once an inode is marked bad, callers should expect normal filesystem operations to fail. `is_bad_inode()` identifies badness by pointer comparison against `bad_inode_ops`.
