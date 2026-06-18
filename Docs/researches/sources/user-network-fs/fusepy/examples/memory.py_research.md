# sources/user-network-fs/fusepy/examples/memory.py

## Purpose
`memory.py` is a simple in-memory fusepy filesystem. It supports one-level files/directories, symlinks, xattrs, chmod/chown, statfs, reads/writes, truncation, rename, and timestamp updates for demonstration.

## Important APIs, Types, and Functions
- `Memory(LoggingMixIn, Operations)`: stores metadata in `self.files`, contents in `self.data`, and a simple fd counter.
- Metadata operations: `getattr`, `chmod`, `chown`, `mkdir`, `rmdir`, `utimens`, `statfs`.
- Data operations: `create`, `open`, `read`, `write`, `truncate`, `unlink`, `rename`.
- Link/xattr operations: `symlink`, `readlink`, `setxattr`, `getxattr`, `listxattr`, `removexattr`.

## Control Flow
Root directory metadata is created at initialization. FUSE calls manipulate dictionaries keyed by full paths. Creating files adds metadata and increments fd. Writes splice bytes at offsets, padding holes with NUL bytes; reads slice content. Directory listing returns every non-root key without hierarchy filtering.

## State and Persistence
All filesystem state is process memory and disappears on unmount. `files[path]` holds stat-like dictionaries and optional `attrs`; `data[path]` holds bytes or symlink targets. Root `st_nlink` is incremented/decremented for mkdir/rmdir.

## Dependencies and Integration Points
It depends on fusepy and standard errno/stat/time collections. It is an example consumer of the high-level `Operations` API and demonstrates dictionary-based stat returns.

## Risks and Edge Cases
It advertises only one-level support but does not strictly enforce it; `readdir('/')` returns stripped full paths for all entries. `rmdir()` does not check `ENOTEMPTY`. `getxattr()`/`removexattr()` return empty/pass for missing attrs instead of ENOATTR. Metadata does not consistently update ctime/mtime on write/truncate/unlink. Symlink target storage may be text while file data is bytes. No permissions or concurrency control are implemented.

## Test Signals
Mount and exercise create/write/read/truncate including sparse offsets, symlink/readlink, xattr round trips, rename, unlink/rmdir, and stat metadata. Tests should document one-level limitations and expected non-POSIX behavior for missing xattrs and non-empty directories.
