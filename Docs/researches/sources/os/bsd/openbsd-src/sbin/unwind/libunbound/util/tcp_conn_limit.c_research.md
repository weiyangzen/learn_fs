# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tcp_conn_limit.c

Implements storage and accounting for per-client TCP connection limits.

Core lifecycle:
- `tcl_list_create` allocates `struct tcl_list` and a regional allocator.
- `tcl_list_delete` traverses the address tree postorder, destroys each node lock, destroys the region, and frees the list.

Configuration loading:
- `tcl_list_apply_cfg` clears the region, initializes the address tree, reads `cfg->tcp_connection_limits`, and initializes parent pointers for closest-netblock lookup.
- `tcl_list_str_cfg` parses a netblock string with `netblockstrtoaddr`, parses the limit with `atoi`, then inserts a node.
- Duplicate address entries are logged at query verbosity if requested.

Runtime accounting:
- `tcl_addr_lookup` returns the closest matching `tcl_addr` netblock node for a client socket address.
- `tcl_new_connection` locks the matched node and increments `count` only if below `limit`; returns false when the limit is reached.
- `tcl_close_connection` decrements the count with an assertion that it was positive.
- If no matching limit node is supplied, new/close operations are effectively allowed/no-op.

Other utilities:
- `tcl_list_get_mem` reports structure plus regional memory.
- `tcl_list_swap_tree` swaps tree and region pointers between two lists; callers are responsible for managing node locks.

Integration points:
- Uses regional allocation for config-owned `tcl_addr` nodes.
- Uses `addr_tree_*` from `dnstree.c` for closest netblock lookup.
- Depends on config parsing, localzone port constants, and networking helpers.
