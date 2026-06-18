# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.c

## Summary
Implements the O2CB nodemanager module and configfs cluster hierarchy. It manages the single active cluster, node configuration, local node activation, IP lookup, network timing attributes, fence method selection, heartbeat group attachment, subsystem dependencies, and module init/exit ordering.

## Main Responsibilities
- Maintain `o2nm_single_cluster` and enforce one active cluster.
- Provide node lookup by node number and IPv4 address with config item references.
- Maintain configured-node bitmap and IP rbtree.
- Create configfs cluster, node, and default heartbeat groups.
- Validate and store node number, IPv4 port, IPv4 address, and local-node flag.
- Start/stop O2NET listening when the local node is enabled/disabled.
- Expose cluster network timing and fencing attributes.
- Pin/unpin configfs items for heartbeat-dependent users.
- Initialize heartbeat, networking, configfs, and O2CB sysfs in module init.

## Key Interfaces
- `o2nm_get_node_by_num()`, `o2nm_get_node_by_ip()`, `o2nm_node_get()`, and `o2nm_node_put()`.
- `o2nm_this_node()` returns the configured local node or invalid node number.
- `o2nm_configured_node_map()` returns the cluster node bitmap.
- `o2nm_depend_item()`, `o2nm_undepend_item()`, `o2nm_depend_this_node()`, and `_undepend_this_node()` wrap configfs dependencies.
- Module init/exit: `init_o2nm()` and `exit_o2nm()`.

## Important Behavior
A node cannot publish its node number until address and port are set, because network code can immediately resolve it. Address insertion rejects duplicates through the rbtree. Setting `local=1` requires all other node attributes and starts the network listener; clearing it stops listening.

Cluster timeout values cannot be changed after peers are connected if they would break negotiated timing. Keepalive must remain below idle timeout. Fence method accepts `reset` or `panic`.

Dropping a node disconnects it, stops local listening if applicable, removes its IP tree entry and node bitmap entry, and releases the config item.

## State and Synchronization
Uses the configfs subsystem mutex for structural changes and `cl_nodes_lock` for node arrays, bitmaps, and IP tree. Node config items provide lifetime references.

## Cross-File Interactions
Creates the heartbeat configfs group from `heartbeat.c`, starts O2NET listeners from `tcp.c`, exposes sysfs through `sys.c`, and uses masklog for cluster diagnostics.

## Risks
The single-cluster global simplifies lookup but means all users assume `o2nm_single_cluster` stability. Node attribute ordering, local-node transitions, configfs dependency lifetimes, and network listener start/stop are the main correctness boundaries.
