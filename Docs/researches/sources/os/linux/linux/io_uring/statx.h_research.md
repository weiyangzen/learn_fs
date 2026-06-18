# File Research: sources/os/linux/linux/io_uring/statx.h

Header for io_uring statx operation.

Key responsibilities:
- Declares statx prep, issue, and cleanup functions.

Important invariant:
- Cleanup must dismiss delayed filename storage captured during prep.
