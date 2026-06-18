# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp.c

## Purpose
Implements the OCFS2 O2CB cluster TCP transport. It manages per-node TCP connections, wire-message framing, synchronous request/status exchange, unsolicited message dispatch, heartbeat-driven connect/disconnect policy, keepalive/idle timeout behavior, and integration with quorum handling.

## Main Responsibilities
- Maintains global per-node state in `o2net_nodes[O2NM_MAX_NODES]`.
- Owns the listening socket, ordered workqueue `o2net_wq`, heartbeat callbacks, and prebuilt handshake/keepalive messages.
- Provides exported send APIs:
  - `o2net_send_message()`
  - `o2net_send_message_vec()`
  - `o2net_fill_node_map()`
  - handler registration/unregistration APIs.
- Converts wire-level system statuses to Linux errno values through `o2net_sys_err_to_errno()`.

## Connection Lifecycle
Each remote node has an `o2net_node` tracking:
- active socket container `nn_sc`
- validity bit `nn_sc_valid`
- persistent transmit error `nn_persistent_error`
- status waiter IDR/list
- delayed connect, connect-expired, and quorum-still-up work.

The higher-numbered node initiates a connection when heartbeat reports a lower-numbered node up. The lower-numbered node accepts only if the peer is heartbeating. `o2net_set_nn_state()` centralizes state transitions, reference management, connected-peer accounting, wakeups for senders, status waiter completion on disconnect, reconnect scheduling, and quorum notifications.

## Socket Container Model
`struct o2net_sock_container` wraps a kernel socket with:
- `kref` lifetime control
- receive page and offset
- socket callbacks
- send mutex
- RX, connect-complete, shutdown, and keepalive work
- idle timer
- debug/stat timing fields when enabled.

`sc_alloc()`, `sc_get()`, `sc_put()`, and `sc_kref_release()` ensure sockets, pages, node references, and debug state are released only after queued work and callback references are gone.

## Wire Protocol and Framing
Incoming data is copied into the per-socket page. `o2net_advance_rx()` first reads and validates the handshake, then repeatedly reads:
1. fixed `struct o2net_msg` header
2. bounded payload up to `O2NET_MAX_PAYLOAD_BYTES`
3. dispatch/status/keepalive handling.

Framing errors, oversized payloads, failed handshakes, EOF, and non-`EAGAIN` receive failures trigger shutdown.

## Send Path
`o2net_send_message_vec()`:
- validates workqueue availability, vector length, payload length, and target node.
- waits until `o2net_tx_can_proceed()` returns either a valid socket or a persistent error.
- allocates a status waiter in the node IDR.
- prepends an `o2net_msg` header with the waiter ID in `msg_num`.
- sends under `sc_send_lock`.
- waits for the peer’s `O2NET_MSG_STATUS_MAGIC`.
- returns translated system status, optionally filling caller status.

This is synchronous and can block on socket readiness, send completion, and remote handler completion.

## Receive Dispatch
`o2net_process_message()` handles:
- `O2NET_MSG_STATUS_MAGIC`: completes a pending status waiter.
- `O2NET_MSG_KEEP_REQ_MAGIC`: sends a keepalive response.
- `O2NET_MSG_KEEP_RESP_MAGIC`: refreshes idle state without further action.
- `O2NET_MSG_MAGIC`: looks up registered handler by `(msg_type, key)`, validates payload length, invokes handler, sends status response, and invokes optional post-handler.

Handlers are stored in an RB tree guarded by `o2net_handler_lock`; handler references are protected by `kref`.

## Handshake and Timeout Validation
`o2net_check_handshake()` requires peers to match:
- `O2NET_PROTOCOL_VERSION`
- O2NET idle timeout
- keepalive delay
- heartbeat write timeout.

Mismatch causes persistent `-ENOTCONN` shutdown to avoid unsafe cluster behavior.

## Keepalive, Idle Timeout, and Quorum
`o2net_sc_reset_idle_timer()` schedules keepalive work and idle timer. Any valid incoming message calls `o2net_sc_postpone_idle()`, which clears timeout/quorum error state if the connection recovered. Idle timeout does not immediately shut down the socket; it marks timeout, reports quorum connection error, schedules delayed still-up quorum work, and restarts the timer.

## Listening and Accept
`o2net_start_listening()` allocates an ordered reclaim-safe workqueue and opens a TCP listening socket. `o2net_accept_many()` drains pending accepts to avoid queued connections being stranded under interrupt moderation. Accepted sockets are validated by source IP, node-number direction, heartbeat state, and duplicate connection checks before a socket container is attached.

## Shutdown
`o2net_stop_listening()` detaches listen callbacks, disconnects all configured nodes, destroys the workqueue, releases the listening socket, and reports local quorum connection error. `o2net_disconnect_node()` sets persistent `-ENOTCONN`, cancels delayed work, and flushes the workqueue.

## Important Dependencies
- OCFS2 cluster heartbeat and node manager.
- O2CB quorum subsystem.
- Linux kernel socket/TCP APIs.
- `idr`, `kref`, workqueues, timers, spinlocks, mutexes.
- `tcp_internal.h` protocol structures and constants.
