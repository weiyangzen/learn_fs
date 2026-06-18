## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read.c

Purpose: implements file and xattr reads.

APIs and flow: `_9p_read` validates fid and negotiated `msize`, initializes op context, starts building `RREAD`, and either copies from cached xattr content or prepares a one-iovec `fsal_io_arg` and calls `fsal_read`. It records I/O stats when a client object is available and returns actual byte count.

State/dependencies: reads from fid object state or xattr cache. Uses request cond/mutex in `async_process_data`, FSAL read completion, client manager, and server stats.

Risks/tests: test `msize` enforcement, xattr offset bounds/read-only mode, partial reads, EOF, FSAL async/sync return behavior, stats byte accounting, and reading without prior open if client permits it.
