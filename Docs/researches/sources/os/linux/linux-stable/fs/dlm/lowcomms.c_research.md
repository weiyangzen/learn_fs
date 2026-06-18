# File Research: sources/os/linux/linux-stable/fs/dlm/lowcomms.c

## Purpose
`lowcomms.c` is the DLM low-level transport layer. It owns kernel sockets, peer address mapping, connection setup/teardown, send buffering, receive buffering, and delivery of complete byte-stream messages to `midcomms`.

It supports TCP and SCTP through `dlm_proto_ops`, selected by `dlm_config.ci_protocol`.

## Core State
- `struct connection`: per-node transport state, including socket, address list, socket mark, write queue, receive leftovers, work items, shutdown waitqueue, and optional `othercon`.
- `struct writequeue_entry`: page-backed outgoing buffer containing one or more `struct dlm_msg` records.
- `struct dlm_msg`: lowcomms message handle with kref lifetime, committed page location, retransmit state, and SRCU index exchange.
- `struct processqueue_entry`: buffered complete incoming bytes queued for DLM processing.

Connections are stored in `connection_hash[CONN_HASH_SIZE]` under SRCU with `connections_lock` protecting hash mutations.

## Receive Path
Socket callbacks queue work:
- `lowcomms_data_ready()` sets `CF_RECV_INTR` and queues receive work.
- `lowcomms_write_space()` clears app-limited send state and queues send work.
- `lowcomms_listen_data_ready()` queues accept work.

`receive_from_sock()` reads nonblocking from the socket, prepends `rx_leftover_buf`, calls `dlm_validate_incoming_buffer()` to find complete messages, stores incomplete tail bytes, and queues `process_dlm_messages()` on `process_workqueue`.

The process queue is bounded with `DLM_MAX_PROCESS_BUFFERS`; when it grows too large, receive work waits for the process queue to drain.

## Send Path
Callers use `dlm_lowcomms_new_msg()` to reserve a message buffer, fill it, then must call `dlm_lowcomms_commit_msg()`. Messages are packed into page-backed writequeue entries.

`send_to_sock()` sends with `MSG_SPLICE_PAGES | MSG_DONTWAIT | MSG_NOSIGNAL`. Partial sends mark an entry dirty. On reconnect, a dirty first entry is dropped so the peer cannot receive the tail of a half-sent DLM message.

`dlm_lowcomms_resend_msg()` duplicates a committed message for midcomms retransmission and marks the original as retransmitting.

## Connection Handling
`dlm_lowcomms_addr()` registers peer addresses and creates connection objects. `nodeid_to_addr()` and `addr_to_nodeid()` translate configured addresses to node ids and socket marks.

`accept_from_sock()` matches incoming sockets to configured peers. If an active socket already exists, the accepted socket is placed in `othercon` to preserve compatibility with crossed simultaneous connects.

`dlm_connect()` creates a kernel socket, applies TCP/SCTP options, binds local cluster addresses, installs callbacks, and calls `kernel_connect()`.

## Protocol Variants
- TCP binds only the first local address and warns when multiple local addresses exist.
- SCTP binds all local addresses, requests the SCTP module, sets a larger receive buffer, and cycles peer addresses.
- TCP shutdown uses `SHUT_WR`; SCTP uses `SHUT_RDWR`.

## Shutdown and Cleanup
`dlm_lowcomms_shutdown()` stops the listener callback, closes the listener, shuts down every peer connection, drains workqueues, closes sockets, cleans write queues, and re-enables connection I/O flags.

`dlm_lowcomms_close()` is called when recovery/fencing knows a node has left. It stops I/O, closes sockets, removes the connection from the SRCU hash, cleans queued messages, and defers freeing through `call_srcu()`.

## Risks and Notes
Correctness depends on message boundary preservation, kref/SRCU lifetime pairing, callback restoration before socket release, and ordering between close/shutdown/workqueue cancellation. `othercon` is explicitly compatibility debt and recursively stopped/closed with the primary connection.
