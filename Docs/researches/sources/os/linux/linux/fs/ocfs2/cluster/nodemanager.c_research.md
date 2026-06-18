# File Research: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.c

OCFS2 cluster nodemanager module. It owns the O2CB configfs cluster hierarchy, singleton cluster registry, node definitions, local-node activation, heartbeat group attachment, sysfs initialization, and module lifecycle.

Global model:
- `o2nm_single_cluster` enforces one active cluster at a time.
- Cluster tracks node array, node bitmap, IPv4 address rb-tree, local-node state, O2Net timing settings, and fence method.

Lookup/exported helpers:
- `o2nm_get_node_by_num()` and `o2nm_get_node_by_ip()` return config-item-referenced nodes.
- `o2nm_configured_node_map()` copies the configured node bitmap.
- `o2nm_this_node()` returns the local node number or invalid node.
- `o2nm_node_get()` / `o2nm_node_put()` wrap config item refs.
- `o2nm_depend_item()` / `undepend_item()` and local-node depend helpers integrate with configfs dependency pinning.

Node configfs:
- Node attributes: `num`, `ipv4_port`, `ipv4_address`, `local`.
- Address and port must be set before node number.
- Setting node number inserts the node into `cl_nodes[]` and bitmap.
- IPv4 address store validates dotted-quad input and inserts into an rb-tree to prevent duplicates.
- Setting `local=1` requires address, port, and number, then starts O2Net listening. Clearing local stops listening for that node.
- Dropping a node disconnects O2Net, stops listening if it was local, erases rb-tree and bitmap entries, and releases the config item.

Cluster configfs:
- Cluster attributes: `idle_timeout_ms`, `keepalive_delay_ms`, `reconnect_delay_ms`, `fence_method`.
- Idle and keepalive timeouts cannot change after peers are connected and must maintain idle > keepalive.
- Fence method supports `reset` and `panic`.

Hierarchy:
- Top-level configfs subsystem name: `cluster`.
- Creating a cluster creates default `node` and `heartbeat` groups.
- Only one cluster can exist; creating a second returns `-ENOSPC`.
- Dropping the cluster removes default groups and clears the singleton pointer.

Module lifecycle:
- `init_o2nm()` initializes heartbeat, O2Net, heartbeat callbacks, configfs subsystem, and O2CB sysfs.
- Exit unregisters heartbeat callbacks, configfs subsystem, sysfs, O2Net, and heartbeat.
