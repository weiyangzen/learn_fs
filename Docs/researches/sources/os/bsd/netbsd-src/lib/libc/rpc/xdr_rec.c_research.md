# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_rec.c

This file implements XDR record marking streams, the framing layer used by connection-oriented RPC over byte streams. It creates an `XDR` backend that reads and writes records made of one or more fragments. Each fragment starts with a 32-bit network-order header: the top bit is `LAST_FRAG`, and the lower 31 bits are the fragment byte count.

The central private state is `RECSTREAM`, stored in `xdrs->x_private`. It contains output buffer pointers, current fragment header position, input buffer pointers, fragment bytes remaining, last-fragment state, callback handles for transport read/write, original send/receive sizes, and nonblocking assembly state including partial header, received byte count, record length, and max-record limit.

`xdrrec_create` allocates and initializes the stream, fixes small buffer sizes to rounded 4000-byte defaults, allocates input/output buffers, installs `xdrrec_ops`, and stores the caller-provided opaque TCP handle plus read/write callbacks.

The XDR ops implement word and byte encode/decode over the record buffer:
- `xdrrec_getlong`, `xdrrec_getbytes`, and `xdrrec_inline` consume bytes within the current fragment and fetch more fragments as needed.
- `xdrrec_putlong`, `xdrrec_putbytes`, and `xdrrec_inline` append to the current output fragment, flushing when full.
- `xdrrec_getpos`/`xdrrec_setpos` support limited repositioning inside buffered data.
- `xdrrec_destroy` frees both buffers and the `RECSTREAM`.

Public record controls are `xdrrec_skiprecord`, `xdrrec_eof`, and `xdrrec_endofrecord`. Skipping drains the current record and aligns the next decode. EOF checks whether buffered data remains after consuming the current record. End-of-record either flushes immediately or seals the current fragment and reserves a new fragment header for batching.

Nonblocking support is provided by `__xdrrec_getrec` and `__xdrrec_setnonblock`. In nonblocking mode, reads assemble a complete record into the input buffer before decode proceeds. It tracks partial headers, rejects zero fragments, rejects fragments or cumulative records above `in_maxrec`, reallocates the input buffer up to the record size, and returns transport status through `enum xprt_stat`.

Internal helpers handle flushing, blocking input refill, byte copying/skipping, fragment header parsing, buffer size rounding, and input buffer reallocation.

Research notes and risks:
- The blocking path does not enforce the nonblocking `in_maxrec` limit; it only rejects a literal zero header in `set_input_fragment`.
- `xdrrec_getpos` treats `tcp_handle` as an fd for `lseek`, which is only meaningful for transports where the opaque handle is actually fd-like.
- Nonblocking full-record buffering protects request size but can reallocate to the configured maximum, so the max-record setting is important for memory pressure.
