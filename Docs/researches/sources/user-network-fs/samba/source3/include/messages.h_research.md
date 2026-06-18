# sources/user-network-fs/samba/source3/include/messages.h

## Purpose
`messages.h` declares Samba source3's intra-process and inter-process messaging API. It is the daemon coordination layer for typed messages between `server_id` endpoints, with tevent integration and support for data blobs, iovecs, file descriptors, broadcast sends, and filtered asynchronous reads.

## Important APIs, Types, And Control Flow
`messaging_init()` creates a `messaging_context`, and helpers expose its local `server_id`, tevent context, and names database. `messaging_register()` and `messaging_deregister()` attach callbacks by message type. Send paths include `messaging_send()`, `messaging_send_buf()`, `messaging_send_iov_from()`, `messaging_send_iov()`, and `messaging_send_all()`. Receive paths use tevent requests via `messaging_filtered_read_send()`/`recv()` and `messaging_read_send()`/`recv()`. `messaging_reinit()` handles forked processes, `messaging_cleanup()` removes stale records, and `messaging_rec_create()` builds received-message objects.

## State And Persistence
State is held in `messaging_context`: registered handlers, local identity, tevent loop, names database, and transport resources. The API can persist process identity/name mappings in the messaging names database and performs cleanup by pid. Large sends can drive a tevent loop even though send functions look synchronous.

## Dependencies And Integration Points
It depends on tevent, NTSTATUS, `server_id`, `DATA_BLOB`, networking headers, iovec/fd passing, and generated `ndr_messaging`. It integrates with smbd, nmbd, winbindd, printing notifications, cache invalidation, debug hooks, and daemon reinit-after-fork code.

## Risks And Test Signals
Risks include assuming send calls are purely synchronous, losing low-priority messages under load, stale registrations after fork, cleanup races for reused pids, fd passing portability, and message version incompatibility. Test signals include register/send/receive round trips, large message delivery with tevent activity, broadcast behavior, low-priority drop tolerance, filtered reads, fd passing, `messaging_reinit()` after fork, stale pid cleanup, and NDR compatibility for message records.
