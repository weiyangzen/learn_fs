# File Research: sources/os/linux/linux/fs/jfs/jfs_inode.c

## Role

Provides basic JFS inode flag translation and new inode allocation/initialization.

## Key Responsibilities

- Maps JFS-specific mode flags to Linux inode flags in `jfs_set_inode_flags()`: immutable, append-only, no-atime, dirsync, and sync.
- Allocates a new VFS inode in `ialloc()`.
- Allocates a disk inode through `diAlloc()`, passing whether the requested mode is a directory.
- Inserts the new inode into the inode hash with `insert_inode_locked()`.
- Initializes owner, saved uid/gid, quota state, inherited JFS flags, file/directory/symlink mode flags, timestamps, generation number, and private JFS inode fields.
- Initializes directory inodes with `IDIRECTORY` and non-directories with `INLINEEA | ISPARSE`, clearing immutable/append inheritance for symlinks.
- Handles allocation failures by dropping quotas, clearing links, discarding new inodes, or putting the inode as appropriate.

## Important Interactions

- Calls `diAlloc()` from `jfs_imap.c` for disk inode assignment and inode extent metadata.
- Calls quota initialization/allocation after VFS ownership setup.
- Reads inherited JFS flags from the parent inode's `mode2`.
- Uses `JFS_SBI(sb)->gengen` to assign inode generation numbers.
- Calls `jfs_set_inode_flags()` after setting JFS mode flags.

## Invariants and Risks

- New inode state must be initialized after successful disk inode allocation but before returning to directory creation/link code.
- Quota allocation happens after the inode is inserted/owned; failure paths must mark `S_NOQUOTA`, clear link count, and discard the inode.
- Symlinks deliberately do not inherit immutable or append-only flags.
- `mode2` stores both JFS-specific high bits and the low inode mode bits.
