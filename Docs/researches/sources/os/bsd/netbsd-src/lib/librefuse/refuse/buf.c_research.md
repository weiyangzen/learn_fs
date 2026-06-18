# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.c

This file implements the FUSE 2.9 buffer-vector helpers. `fuse_buf_size` totals buffer sizes, and `fuse_buf_copy` copies between source and destination `fuse_bufvec`s while advancing vector indices and offsets.

Copy paths handle memory-to-memory with `memmove`, fd-to-memory with `read`/`pread`, memory-to-fd with `write`/`pwrite`, and fd-to-fd through a page-sized temporary heap buffer. EINTR is retried, partial success is returned rather than converted into failure, and `FUSE_BUF_FD_SEEK` selects positioned I/O.

Integration points: used by versioned `read_buf`/`write_buf` operation support from `fs.c`. Risks include ignored splice flags, short I/O behavior, unbounded `size_t` totals, and the fact that fd-to-fd cannot recover data already read but not written.
