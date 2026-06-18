# File Research: sources/local-fs/xfsprogs/db/namei.h

## Purpose
Declares path walking and directory listing interfaces for xfs_db.

## Interfaces
- `path_walk(rootino, path)` navigates to a path and sets the IO cursor.
- `dir_emit_t` defines callbacks for directory entry enumeration.
- `listdir(tp, dp, dir_emit, private)` enumerates a directory through a callback.

## Dependencies
Requires libxfs transaction/inode and directory type definitions.
