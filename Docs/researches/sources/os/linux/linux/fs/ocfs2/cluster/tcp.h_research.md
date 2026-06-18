# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp.h

## Purpose
Public header for the OCFS2 cluster TCP transport. It defines the on-wire message header, payload limits, timeout defaults, public send/handler APIs, lifecycle entry points, and debugfs hooks.

## Key Types
- `struct o2net_msg`: fixed network message header followed by flexible payload:
  - `magic`
  - `data_len`
  - `msg_type`
  - `sys_status`
  - `status`
  - `key`
  - `msg_num`
  - `buf[]`
- `o2net_msg_handler_func`: called for incoming application messages.
- `o2net_post_msg_handler_func`: optional post-processing callback after status send.

## Limits and Defaults
- `O2NET_MAX_PAYLOAD_BYTES` is one page minus `struct o2net_msg`.
- Default reconnect and keepalive delay: 2000 ms.
- Default idle timeout: 30000 ms.
- `O2NET_TCP_USER_TIMEOUT` is set to `0x7fffffff`.

## Link Failure Helper
`o2net_link_down()` classifies socket state and selected errno values as link failures. It treats non-established/non-close-wait sockets and errors such as `-ECONNREFUSED`, `-ENOTCONN`, `-ECONNRESET`, and `-EPIPE` as down.

## Public API Surface
- Message send:
  - `o2net_send_message()`
  - `o2net_send_message_vec()`
- Handler management:
  - `o2net_register_handler()`
  - `o2net_unregister_handler_list()`
- Connectivity:
  - `o2net_fill_node_map()`
  - `o2net_num_connected_peers()`
  - `o2net_disconnect_node()`
- Heartbeat/listener lifecycle:
  - `o2net_register_hb_callbacks()`
  - `o2net_unregister_hb_callbacks()`
  - `o2net_start_listening()`
  - `o2net_stop_listening()`
- Module lifecycle:
  - `o2net_init()`
  - `o2net_exit()`

## Debugfs Hooks
Declares debugfs setup/teardown and tracking hooks for send tracking and socket containers. When `CONFIG_DEBUG_FS` is disabled, all hooks compile to no-ops.
