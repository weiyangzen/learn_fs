# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp_internal.h

## Summary
Defines private O2CB TCP transport wire constants and in-memory state shared by `tcp.c` and related debug/stat code. It contains message magic values, protocol version history, handshake layout, per-node state, per-socket state, handler descriptors, status-wait records, and debug send-tracking structures.

## Main Responsibilities
- Define wire magic values for normal messages, status replies, keepalive requests, and keepalive responses.
- Define `O2NET_PROTOCOL_VERSION` and document historical protocol/locking-semantic changes.
- Define `struct o2net_handshake` used to validate protocol and timeout compatibility.
- Define `struct o2net_node` for per-peer connection, error, timeout, wait, status-id, and delayed-work state.
- Define `struct o2net_sock_container` for socket lifetime, callbacks, receive framing, idle/keepalive work, and send locking.
- Define `struct o2net_msg_handler` for rb-tree handler registration.
- Define transport-level system errors and `struct o2net_status_wait` for synchronous request completion.
- Define optional debugfs timing and send-tracking fields.

## Key Interfaces
This header has no exported functions. Its key data contracts are:
- `o2net_handshake`: protocol version, connector id, heartbeat timeout, idle timeout, keepalive delay, and reconnect delay.
- `o2net_node`: `nn_sc`, `nn_sc_valid`, `nn_persistent_error`, `nn_timeout`, status `idr`, waitqueue, and connect/expiry/still-up delayed work.
- `o2net_sock_container`: socket reference, node reference, receive/connect/shutdown work, idle timer, keepalive work, receive page offset, original socket callbacks, message identity, and `sc_send_lock`.
- `o2net_system_error`: remote status classes that map to local errno values.

## Important Behavior
The protocol version is not just a packet-format version; comments state it historically covered filesystem locking semantics too. Version 11 introduced separate filesystem locking negotiation in DLM join, reducing the need to bump this transport protocol for filesystem lock changes.

The per-node comments describe critical lifecycle rules: `nn_sc` is set when a socket container is allocated and connection begins; `nn_sc_valid` becomes true only after handshake success; `nn_persistent_error` makes transmit fail immediately; and generation changes wake waiters on `nn_sc_wq`. Delayed connect work can requeue itself, so shutdown must first set state to prevent new connects, then cancel work and flush.

The per-socket comments document why work items hold references and why shutdown can be queued both by explicit state changes and by socket callbacks. Teardown must remove the socket from the node before waiting on work, or shutdown work can detach the socket and rearm itself.

## State and Synchronization
`o2net_node` uses `nn_lock` for node state and status lists, `nn_sc_wq` for transmit waiters, and delayed work for connect retry, connect expiry, and quorum still-up checks. `o2net_sock_container` uses `kref` for lifetime, socket callback locks indirectly through `tcp.c`, a timer for idle timeout, delayed work for keepalive, and `sc_send_lock` to serialize socket writes.

## Cross-File Interactions
`tcp.c` directly allocates, mutates, and tears down these structures. The message sizing depends on `tcp.h`'s `struct o2net_msg`. DLM code indirectly depends on the protocol version and message error semantics because DLM messages are transported over this layer.

## Risks
This header encodes concurrency and lifecycle invariants rather than mere layout. Misinterpreting `nn_sc` versus `nn_sc_valid`, failing to hold references around queued work, or changing protocol/timeout fields without matching handshake validation can break cluster liveness. The fixed one-page payload model ties `O2NET_MAX_PAYLOAD_BYTES`, DLM migratable lockres sizing, and receive-buffer safety together.
