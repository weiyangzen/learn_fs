# File Research: sources/os/linux/linux/fs/dlm/lowcomms.c

## Role

`lowcomms.c` is the DLM low-level transport layer. It owns kernel sockets, address resolution, connection setup/teardown, send buffering, receive buffering, and the handoff of validated byte streams to `midcomms`.

It supports TCP and SCTP, selected by `dlm_config.ci_protocol`, and deliberately sends from workqueues instead of caller context so DLM locking paths do not block on socket flow control.

## Core State

The main structure is `struct connection`, keyed by nodeid in `connection_hash` under SRCU. It stores:
- active `struct socket *sock`
- per-node address list, socket mark, and retry index
- send/receive work items
- a page-backed write queue
- leftover receive bytes for partial DLM messages
- `othercon`, used for crossed incoming/outgoing connection races

`struct writequeue_entry` owns a page of outgoing bytes and a list of `struct dlm_msg` records that refer to messages packed into that page. Krefs keep pages/messages alive for retransmission support in midcomms.

## Address and Connection Handling

`dlm_lowcomms_addr()` adds configured peer addresses and creates a connection object if needed. `nodeid_to_addr()` and `addr_to_nodeid()` translate between DLM nodeids and socket addresses, honoring per-node marks.

Accepted sockets are matched to configured peer addresses. If a connection already exists, the incoming socket is stored in `othercon`, preserving backward-compatible handling of simultaneous connects.

`dlm_connect()` creates a kernel socket, binds it to local cluster address state, applies TCP/SCTP options, installs lowcomms callbacks, and calls `kernel_connect()`.

## Receive Path

Socket callbacks set flags and queue work:
- `lowcomms_data_ready()` queues receive work.
- `lowcomms_write_space()` clears application-limited state and queues send work.
- `lowcomms_listen_data_ready()` queues listener accept work.

`receive_from_sock()` reads nonblocking into a process queue buffer, prepends any previous leftover bytes, asks `dlm_validate_incoming_buffer()` how many complete messages exist, saves incomplete tail bytes, then queues `process_dlm_messages()`.

The process queue is bounded by `DLM_MAX_PROCESS_BUFFERS`; if it grows too large, receive work waits for the process queue to drain to avoid unbounded memory growth.

## Send Path

Callers allocate messages through `dlm_lowcomms_new_msg()`, fill returned memory, then must call `dlm_lowcomms_commit_msg()`. Messages are packed into page-sized write queue entries when space permits.

`send_to_sock()` sends page bytes with `MSG_SPLICE_PAGES | MSG_DONTWAIT | MSG_NOSIGNAL`. Partial sends mark entries dirty; if a dirty entry is interrupted by connection close, the whole entry is dropped so a peer never sees the remainder of a half message after reconnect.

`dlm_lowcomms_resend_msg()` creates a duplicate queued message from an original committed message and marks the original as retransmitting.

## Protocol Variants

The `dlm_proto_ops` table abstracts TCP and SCTP:
- TCP binds only the first local address and warns on multihoming.
- SCTP binds all local addresses and uses a larger receive buffer.
- TCP uses `SHUT_WR`; SCTP uses `SHUT_RDWR`.

## Shutdown and Cleanup

`dlm_lowcomms_shutdown()` stops listener callbacks, closes the listener, shuts down all peer connections, drains workqueues, closes sockets, cleans write queues, then re-enables connection I/O state.

`dlm_lowcomms_close()` is used when recovery knows a node has left. It stops I/O, closes the socket(s), removes the connection from the hash, frees queued messages, and releases objects through SRCU callbacks.

## Important Behaviors and Invariants

- Message allocation and commit carry an SRCU read-side section across the caller fill path.
- Send work is suppressed while `CF_APP_LIMITED` or `CF_IO_STOP` is set.
- Receive parsing accepts complete DLM messages only and preserves leftovers for the next read.
- `othercon` exists only for connection race compatibility and is recursively stopped/closed with the primary connection.
- Socket callbacks must be restored before socket release to avoid callbacks into freed DLM state.

## Research Notes

Read completely. This file is the transport foundation used by `midcomms.c`; correctness hinges on message boundary preservation, kref lifetime rules, SRCU connection lifetime, and shutdown ordering.
