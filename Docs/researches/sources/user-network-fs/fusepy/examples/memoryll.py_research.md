# sources/user-network-fs/fusepy/examples/memoryll.py

## Purpose
`memoryll.py` is a low-level fusepy example using `fusell.FUSELL` rather than the high-level `Operations` API. It demonstrates inode-based request/reply handling for an in-memory filesystem.

## Important APIs, Types, and Functions
- `Memory(FUSELL)`: implements low-level callbacks.
- `init()`: initializes inode counter, attrs, data, parent map, and child name maps with root inode 1.
- `create_ino()`: allocates monotonically increasing inode numbers.
- Lookup/metadata: `getattr`, `lookup`, `setattr`.
- Namespace operations: `mkdir`, `mknod`, `readdir`, `rename`.
- File operations: `open`, `read`, `write`.
- Reply helpers from `FUSELL`: `reply_attr`, `reply_entry`, `reply_err`, `reply_open`, `reply_buf`, `reply_readdir`, `reply_write`, and `req_ctx`.

## Control Flow
FUSE low-level callbacks receive request handles and inode numbers. The code looks up attrs or child names, builds reply dictionaries, and explicitly calls reply methods for every path. Create-like operations use `req_ctx(req)` to set uid/gid. `setattr()` applies only fields listed in `to_set`, preserving file type bits for mode changes.

## State and Persistence
State is in-memory and inode-indexed: `attr[ino]`, `data[ino]`, `parent[ino]`, and `children[parent][name]`. It is lost on unmount. Root starts as inode 1 with mode `S_IFDIR | 0o777`.

## Dependencies and Integration Points
It depends on `fusell.FUSELL`, low-level FUSE semantics, stat helpers (`S_IFMT`, `S_IMODE`, `S_IFDIR`), errno, and time. It is an example of raw request/reply integration rather than the high-level fusepy wrapper.

## Risks and Edge Cases
The implementation is intentionally partial. `mknod()` increments the parent directory link count even for non-directories, which is not POSIX-correct. `write()` truncates data after `off + len(buf)` rather than preserving existing suffix, unlike `memory.py`. There is no unlink/rmdir/release, no permission model, no empty-directory checks, and debugging uses `print()` in callbacks. Inode maps can become inconsistent for complex rename cases.

## Test Signals
Low-level tests should mount and exercise lookup/getattr, mkdir/mknod, read/write offsets, readdir offsets, rename across parents, and setattr mode preservation. Compare behavior with `memory.py` to document intentional differences and incomplete POSIX semantics.
