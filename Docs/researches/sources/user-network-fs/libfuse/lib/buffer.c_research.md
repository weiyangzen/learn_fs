# sources/user-network-fs/libfuse/lib/buffer.c

`buffer.c` implements the `fuse_buf` and `fuse_bufvec` data movement primitives declared in `fuse_common.h`. It supports memory-to-memory, memory-to-fd, fd-to-memory, fd-to-fd, and optional splice-based copies while maintaining vector cursors.

Exported functions are `fuse_buf_size` and `fuse_buf_copy`. Internal helpers are `min_size`, `fuse_buf_write`, `fuse_buf_read`, `fuse_buf_fd_to_fd`, `fuse_buf_splice`, `fuse_buf_copy_one`, `fuse_bufvec_current`, and `fuse_bufvec_advance`.

`fuse_buf_copy` loops over current source and destination buffers, copies the minimum remaining segment, advances both vector cursors, and stops on EOF, short copy, exhausted vector, or error. Memory copies use `memcpy`/`memmove`; fd paths use `read`/`write` or `pread`/`pwrite` when seek flags are set; fd-to-fd uses splice unless disabled/unavailable, with a bounce-buffer fallback. It mutates `idx`/`off`, does not own file descriptors or memory, and affects fd position for non-seek buffers.

Risks include partial-copy semantics where errors after progress return byte counts, short I/O without retry flags, splice `EINVAL` fallback versus forced splice errors, cursor misuse, and total-size saturation to `SIZE_MAX`. Test signals include memory overlap, seek/non-seek fd copies, retry behavior, splice fallback/force, multi-buffer cursor advancement, self-copy, EOF, partial errors, and size overflow.
