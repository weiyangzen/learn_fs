# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.c

## Summary
Implements the O2CB/OCFS2 TCP transport layer. It owns node-to-node socket lifecycle, protocol handshakes, framed message send/receive, synchronous status waits, message handler registration, keepalive and idle-timeout behavior, heartbeat callbacks, listening/accepting, outbound connect attempts, debug/stat tracking hooks, and quorum notifications on connection failure or recovery.

## Main Responsibilities
- Maintain per-node `struct o2net_node` connection state and per-socket `struct o2net_sock_container` lifetime/refcounting.
- Register and unregister typed message handlers in an rb-tree keyed by message type and cluster key.
- Send payload vectors as `struct o2net_msg` frames and wait for remote handler status replies.
- Receive and demultiplex status, keepalive request/response, and application messages from a single page buffer per socket.
- Negotiate protocol and timing parameters through the initial `struct o2net_handshake`.
- Drive active connects from the higher-numbered node and passive accepts from the lower-numbered node.
- Integrate heartbeat up/down callbacks with connect retry, disconnect, and quorum state.
- Start and stop the ordered `o2net` workqueue and listening socket.

## Key Interfaces
- `o2net_send_message_vec()` and `o2net_send_message()` are the exported synchronous transmit APIs.
- `o2net_register_handler()` and `o2net_unregister_handler_list()` manage receive handlers.
- `o2net_fill_node_map()` reports currently reachable peer nodes.
- `o2net_start_listening()` and `o2net_stop_listening()` manage the local TCP listener.
- `o2net_register_hb_callbacks()` and `o2net_unregister_hb_callbacks()` attach transport behavior to heartbeat events.
- `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()` expose lifecycle and status helpers.

## Important Behavior
Messages are framed with magic, payload length, message type, key, message id, system status, and handler status. Transmit allocates a message id from the target node's `idr`, sends the header plus caller vectors under `sc_send_lock`, then waits on `ns_wq` until the receive path completes the matching status wait. If the remote side reports a transport/system condition, that is translated through `o2net_sys_err_to_errno()` before any handler status is returned.

Receive is incremental and nonblocking. Before the handshake completes, `o2net_advance_rx()` reads exactly a handshake and validates protocol version, idle timeout, keepalive delay, and heartbeat write timeout. After that, it reads a message header, validates payload length against `O2NET_MAX_PAYLOAD_BYTES`, reads the payload, and calls `o2net_process_message()`. Any framing error or non-EAGAIN receive failure shuts down the socket.

The socket callback layer queues work before invoking original socket callbacks. `data_ready` queues receive work; `state_change` queues connect-complete work on `TCP_ESTABLISHED` and shutdown work on other terminal states. Callback unregistration restores the original socket callbacks and drops the callback-held socket-container reference.

Connection establishment is deliberately asymmetric: the higher numbered node initiates outbound connects when heartbeat says the lower numbered node is alive; the lower numbered node accepts only if the connecting peer is known, lower/higher ordering is correct, and heartbeat confirms the peer. This prevents duplicate cross-connects.

Keepalive uses a delayed work item to send `O2NET_MSG_KEEP_REQ_MAGIC` and a timer for idle detection. Idle timeout does not immediately close the socket; it marks the node timed out, notifies quorum, queues delayed "still up" work, and resets the idle timer. Any later message activity clears that timeout and tells quorum the connection is up again.

## State and Synchronization
Per-node state is protected by `nn_lock`; handler tree access uses `o2net_handler_lock`; socket callback mutation uses `sk_callback_lock`; socket sends use `sc_send_lock`; work items hold socket-container references while queued. Pending sends are tracked in `nn_status_idr` and `nn_status_list`. The ordered workqueue serializes most blocking transport work, and shutdown carefully detaches callbacks before socket shutdown and workqueue teardown.

## Cross-File Interactions
This file is the transport used by the OCFS2 DLM and cluster modules. It depends on nodemanager for node numbers/IP configuration, heartbeat for node up/down events, quorum for fencing decisions, `tcp_internal.h` for private state and wire constants, `tcp.h` for exported message APIs, and debugfs helpers for optional transport state exposure. DLM files such as `dlmast.c` send and receive DLM messages through these APIs.

## Risks
Correctness depends on exact connection state transitions and reference ownership: queued work, socket callbacks, timers, and node state can race during shutdown. Handler status waits must always be completed on disconnect to avoid blocked senders. Handshake timeout mismatches are treated as fatal because inconsistent liveness windows can cause split-brain or corruption. The receive page is only valid during handler execution, so handlers must not retain pointers into it. The ordered workqueue and `memalloc_nofs_save()` usage are important to avoid filesystem reclaim recursion during socket allocation.
