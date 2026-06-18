# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.h

## Summary
Defines the public O2CB TCP transport API and the common network message header used by OCFS2 cluster components. It exposes send, handler registration, heartbeat/listener lifecycle, connected-node discovery, and optional debugfs hooks.

## Main Responsibilities
- Define `struct o2net_msg`, the framed network message header plus flexible payload buffer.
- Define handler and post-handler callback signatures for incoming message processing.
- Publish payload and timeout constants, including default reconnect, keepalive, idle, and TCP user-timeout values.
- Provide `o2net_link_down()` for classifying socket/errors as connection-loss conditions.
- Declare exported transport lifecycle, send, handler, and heartbeat/listener functions.
- Hide debugfs operations behind no-op inline stubs when `CONFIG_DEBUG_FS` is disabled.

## Key Interfaces
- `o2net_send_message()` and `o2net_send_message_vec()` send one message and optionally return remote handler status.
- `o2net_register_handler()` registers a message type/key callback with a maximum accepted payload length and optional post callback.
- `o2net_unregister_handler_list()` unregisters a caller-owned list of registered handlers.
- `o2net_fill_node_map()` fills a bitmap of currently connected peers.
- `o2net_start_listening()`, `o2net_stop_listening()`, and `o2net_disconnect_node()` control per-node network connectivity.
- `o2net_register_hb_callbacks()` and `o2net_unregister_hb_callbacks()` connect the transport to cluster heartbeat.

## Important Behavior
`O2NET_MAX_PAYLOAD_BYTES` is capped at one page minus the header size, matching the transport implementation's one-page receive buffer. The link-down helper treats non-established/non-close-wait sockets and selected negative errors as loss of connection, while nonnegative results are considered successful. The driver state enum distinguishes uninitialized and ready states for users that need coarse transport readiness.

## State and Synchronization
This header does not own runtime state. It forward-declares `struct o2net_send_tracking` and `struct o2net_sock_container` so debugfs helpers can observe transport internals without exposing their definitions publicly.

## Cross-File Interactions
`tcp.c` implements the declarations. `tcp_internal.h` supplies private constants and structures. DLM and other OCFS2 cluster modules include this header to register message handlers and exchange cluster messages.

## Risks
All callers must respect the maximum payload size and must not assume asynchronous completion: the send API blocks waiting for a remote status reply or connection failure. Handler callbacks receive a buffer owned by the transport receive page and cannot retain payload pointers beyond the callback. `o2net_link_down()` is intentionally conservative and any changes to its error list affect DLM recovery and quorum behavior.
