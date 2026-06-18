# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp_internal.h

## Purpose
Internal transport definitions for OCFS2 O2CB TCP. It captures message magic values, protocol version, handshake layout, per-node/socket state, handler tracking, status waiters, and debug send tracking.

## Wire Constants
Defines message magic values:
- `O2NET_MSG_MAGIC`
- `O2NET_MSG_STATUS_MAGIC`
- `O2NET_MSG_KEEP_REQ_MAGIC`
- `O2NET_MSG_KEEP_RESP_MAGIC`

`O2NET_PROTOCOL_VERSION` is `11`, with comments documenting historical protocol changes and explaining that version 11 separates filesystem locking negotiation from the transport protocol.

## Handshake
`struct o2net_handshake` includes:
- protocol version
- connector ID
- heartbeat timeout
- idle timeout
- keepalive delay
- reconnect delay.

These values are validated during connection setup to avoid unsafe mixed-timeout cluster behavior.

## Per-Node State
`struct o2net_node` stores:
- lock-protected socket container pointer and validity bit
- persistent error for future sends
- timeout flag
- waitqueue for socket state changes
- IDR/list for pending status waiters
- delayed connect, connect-expired, and quorum still-up work.

## Socket State
`struct o2net_sock_container` stores:
- kref
- socket and node pointer
- RX/connect/shutdown/keepalive work
- idle timer
- handshake state
- receive page and offset
- saved original socket callbacks
- current message key/type for stats/debug
- send mutex
- optional debug/stat timing counters.

## Handler and Status Wait Structures
`struct o2net_msg_handler` is the RB-tree entry for registered handlers, keyed by message type and key, with max payload length, handler callbacks, kref, and unregister-list linkage.

`struct o2net_status_wait` records a pending synchronous send’s system status, user status, IDR ID, waitqueue, and per-node list linkage.

## System Error Enum
`enum o2net_system_error` defines wire-level transport statuses:
- none
- no handler
- overflow
- died.

These are translated by tcp.c into Linux errno values.

## Debug Tracking
`struct o2net_send_tracking` records task, socket container, message ID/type/key, target node, and timing points when debugfs is enabled; otherwise it is reduced to a dummy field.
