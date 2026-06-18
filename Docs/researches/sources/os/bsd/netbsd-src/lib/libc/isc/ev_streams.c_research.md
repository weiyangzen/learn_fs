# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/ev_streams.c

ISC eventlib asynchronous stream I/O implementation.

Always-built helper:
- `evConsIovec(buf, cnt)` returns a populated `struct iovec`.

Most stream implementation is excluded when `_LIBC` is defined:
- `evWrite` and `evRead` allocate an `evStream`, register FD readiness callbacks, copy the caller iovec array, and link the stream into the event context.
- `evTimeRW`/`evUntimeRW` attach or detach idle timer handling.
- `evCancelRW` unlinks streams from active and done lists, deselects FDs, frees copied iovecs, and releases the stream.
- `copyvec`, `consume`, `done`, `writable`, and `readable` implement scatter/gather progress tracking and completion notification.

Dependencies: `eventlib_p.h`, `isc/eventlib.h`, `isc/assertions.h`, `fd_setsize.h`, memory-cluster allocation helpers.
