# sources/user-network-fs/fusepy/examples/loopback.py

## Purpose
`loopback.py` is a fusepy passthrough filesystem. It mirrors operations on a real root directory into a mounted FUSE view, forwarding most filesystem calls to Python `os` functions.

## Important APIs, Types, and Functions
- `Loopback(LoggingMixIn, Operations)`: wraps a real path and serializes read/write using a `Lock`.
- `__call__(op, path, *args)`: rewrites every FUSE path to `self.root + path` before normal dispatch.
- Direct aliases: `chmod`, `chown`, `mkdir`, `mknod`, `open`, `readlink`, `rmdir`, `unlink`, `utimens`.
- Implemented methods: `access`, `create`, `flush`, `fsync`, `getattr`, `link`, `read`, `readdir`, `release`, `rename`, `statfs`, `symlink`, `truncate`, `write`.

## Control Flow
The main block takes `root` and `mount`, constructs `Loopback(realpath(root))`, and mounts it in the foreground with `allow_other=True`. Every incoming operation is path-rewritten before reaching the method. File handles returned by `os.open()` are reused for read/write/flush/release. Read and write operations seek then transfer under `rwlock`.

## State and Persistence
All persistent state is the underlying real filesystem. In-memory state is limited to `root` and a lock. FUSE operations can mutate real files, directories, links, modes, owners, timestamps, and filesystem contents.

## Dependencies and Integration Points
It depends on fusepy and Python `os`, `os.path.realpath`, and `threading.Lock`. It relies on the kernel and underlying filesystem permissions. `allow_other` expands visibility to other users if configured.

## Risks and Edge Cases
Path rewriting by string concatenation assumes FUSE supplies absolute paths beginning with `/`; it does not defend against unusual paths or symlink escape because operations are delegated to the underlying filesystem. `truncate()` opens in text mode `'r+'`, which can be wrong for binary data or Python 3 newline handling. `getxattr` and `listxattr` are disabled. `link()`/`rename()`/`symlink()` argument order is intentionally adapted but easy to misunderstand. The read/write lock serializes only those operations, not metadata mutations.

## Test Signals
Mount over a temp root and compare create/read/write/rename/link/symlink/statfs behavior with direct filesystem operations. Test binary truncate behavior, concurrent reads/writes, permission failures, and `allow_other` configuration errors.
