# sources/user-network-fs/fusepy/examples/ioctl.py

## Purpose
`ioctl.py` is a fusepy in-memory example demonstrating FUSE ioctl callback handling. It creates a simple one-level filesystem and implements one read/write ioctl command that reads a 32-bit integer from the caller buffer, increments it, and writes it back.

## Important APIs, Types, and Functions
- `Ioctl(LoggingMixIn, Operations)`: minimal in-memory filesystem with ioctl support.
- `__init__()`: initializes root metadata, file map, byte data, and fd counter.
- `create()`, `open()`, `getattr()`, `read()`, `readdir()`: basic operations for files.
- `ioctl(path, cmd, arg, fh, flags, data)`: recognizes `IOWR(ord('M'), 1, ctypes.c_uint32)`, copies four bytes from `data`, unpacks little-endian uint32, increments, and writes back. Unknown commands raise `ENOTTY`.

## Control Flow
The example mounts `Ioctl()` in the foreground. Users create a file in the mount, then run the C helper. FUSE dispatches ioctl into Python with a raw pointer. The handler uses `ctypes.memmove()` and `struct` to read/write the caller’s buffer.

## State and Persistence
Filesystem state is process-local memory: `files` metadata, `data` contents, and monotonic `fd`. It is lost on unmount. The ioctl does not persist changes to file data; it only mutates the ioctl argument buffer.

## Dependencies and Integration Points
It depends on fusepy, `ioctl_opt.IOWR`, ctypes, struct, and the companion `ioctl.c` for demonstration. It must run on a platform whose ioctl encoding matches `ioctl_opt`.

## Risks and Edge Cases
The handler assumes `data` points to at least four bytes and uses little-endian unpacking. There is no write method, so data is mostly empty unless extended. `read()` ignores missing path checks and returns from defaultdict. No directory hierarchy or permission checks are implemented.

## Test Signals
Mount, create a file, run the C helper, and assert returned integer increments. Test unknown ioctl command returns `ENOTTY`, multiple created files appear in `readdir`, and unmounted/remounted state is empty.
