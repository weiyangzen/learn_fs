# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_node.c

`o2cb` node add/remove operations.

`add-node` parses optional `--ip`, `--port`, and `--number`, discovers IPv4 address from hostname when omitted, validates node number range and uniqueness, defaults port to 7777, adds the node to the named cluster, and stores IP/port/number. `remove-node` deletes a node by cluster and node name.

The IP auto-discovery path uses `getaddrinfo()` constrained to IPv4 TCP addresses.
