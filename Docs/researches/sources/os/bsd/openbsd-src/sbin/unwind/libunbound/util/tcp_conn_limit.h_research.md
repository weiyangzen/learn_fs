# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.h

Defines the TCP connection limit data structures and API.

Key structures:
- `struct tcl_list`: regional allocator plus address `rbtree_type`.
- `struct tcl_addr`: address tree node, quick lock, configured limit, and current count.

Public API:
- `tcl_list_create`, `tcl_list_delete`.
- `tcl_list_apply_cfg`.
- `tcl_new_connection`, `tcl_close_connection`.
- `tcl_addr_lookup`.
- `tcl_list_get_mem`.
- `tcl_list_swap_tree`.

Usage contract:
- A caller first looks up the client address, then passes the returned `tcl_addr*` to connection open/close accounting.
- Passing NULL to `tcl_new_connection` permits the connection.
- Node locks protect `limit`/`count` mutation.
