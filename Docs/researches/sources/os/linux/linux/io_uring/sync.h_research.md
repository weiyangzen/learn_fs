# File Research: sources/os/linux/linux/io_uring/sync.h

Header for io_uring sync-style operations.

Key responsibilities:
- Declares prep and issue functions for sync_file_range, fsync, and fallocate.

Important invariant:
- All declared operations are blocking VFS operations and are prepared to run asynchronously.
