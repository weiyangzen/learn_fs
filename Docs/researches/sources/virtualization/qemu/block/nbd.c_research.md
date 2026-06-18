# File Research: sources/virtualization/qemu/block/nbd.c

## Purpose
Implements QEMU’s NBD client block driver for `nbd`, `nbd+tcp`, and `nbd+unix` protocols. It parses NBD URLs/options, negotiates exports, translates block I/O to NBD commands, handles structured replies and block status, supports TLS, reconnects after transient disconnects, and participates in yank/cancel handling.

## Main Entry Points
- `nbd_open()` initializes state, parses options, registers yank support, creates the client connection, performs negotiation, and enables retry.
- `nbd_co_do_establish_connection()` connects and negotiates with the NBD server, registers yank, applies negotiated export information, and switches the channel to nonblocking coroutine mode.
- `nbd_co_send_request()` allocates one of 16 request slots, handles reconnect attempts, serializes request sending, and writes optional payload data.
- `nbd_receive_replies()` and `nbd_co_receive_one_chunk()` demultiplex replies by cookie and validate simple/structured reply headers.
- `nbd_client_co_preadv()`, `nbd_client_co_pwritev()`, `nbd_client_co_pwrite_zeroes()`, `nbd_client_co_flush()`, `nbd_client_co_pdiscard()`, and `nbd_client_co_block_status()` implement block driver I/O callbacks.
- `nbd_parse_filename()`, `nbd_parse_uri()`, `nbd_process_options()`, and `nbd_config()` map filename and QDict options into a `SocketAddress` and connection parameters.
- `nbd_close()`, `nbd_cancel_in_flight()`, `nbd_yank()`, and timer callbacks manage shutdown, cancellation, and reconnect/open timeout behavior.

## Internal Mechanics
`BDRVNBDState` stores the current `QIOChannel`, negotiated `NBDExportInfo`, request slot table, in-flight count, reconnect/open timers, send and receive coroutine mutexes, socket/TLS/export options, and the `NBDClientConnection`.

Requests use cookies derived from request slot indexes. Sending is protected by `send_mutex`; receiving is protected by `receive_mutex`. If a coroutine receives another request’s cookie, it wakes the owning coroutine and waits until its own reply is available. Structured replies are consumed chunk-by-chunk with an iterator that records fatal channel errors separately from per-request NBD errors.

The read path supports simple replies, `OFFSET_DATA`, and `OFFSET_HOLE`, including zero-filling holes and padding reads beyond an unaligned server EOF. Block status requests parse narrow and extended status chunks, clamp noncompliant lengths, map `NBD_STATE_HOLE`/`NBD_STATE_ZERO` to QEMU block status flags, and optionally expose `x-dirty-bitmap`/`qemu:allocation-depth` behavior.

Reconnect uses a state machine: connected, connecting with wait, connecting without wait, and quit. After socket `-EIO`, existing requests can pause for `reconnect-delay`; after that timer expires, delayed and future requests fail until a connection succeeds. Open timeout uses a separate timer during initial open.

## Dependencies
Uses QEMU NBD protocol/client helpers, QIO channels, QAPI socket/TLS visitors, QCrypto TLS credentials, block driver APIs, coroutine mutexes/queues, timers, yank infrastructure, QDict option parsing, GLib URI parsing, and tracepoints.

## Risks and Notes
The driver has strict concurrency invariants around `requests_lock`, `send_mutex`, `receive_mutex`, request cookies, and `s->reply.cookie`; protocol violations usually poison the channel. Reconnect only retries after errors treated as socket I/O failures, not semantic protocol errors. Open and reconnect timers must be deleted before drain/close, and the code asserts that no timers survive context changes. The block layer still uses sector-rounded sizes in places, so the driver explicitly handles tail reads/status beyond the advertised NBD export size.
