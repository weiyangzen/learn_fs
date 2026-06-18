# File Research: sources/os/linux/linux/io_uring/splice.h

Header for io_uring splice and tee operations.

Key responsibilities:
- Declares prep and issue functions for tee and splice.
- Declares splice cleanup for fixed input resource references.

Important invariant:
- Cleanup is needed only when the operation retained a fixed-file resource node.
