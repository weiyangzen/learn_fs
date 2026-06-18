# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/nodemanager.h

## Summary
Defines internal O2CB nodemanager structures and exported lookup/dependency APIs.

## Main Responsibilities
- Define fencing method enum.
- Define `struct o2nm_node` with configfs item, name, node number, IPv4 address/port, rbtree node, local flag, and attribute bitmap.
- Define `struct o2nm_cluster` with configfs group, local-node state, node lock, node table, IP tree, timeouts, fence method, and node bitmap.
- Declare the single active cluster pointer and public nodemanager helpers.

## Key Interfaces
- `o2nm_this_node()` reports local identity.
- Node lookup and ref helpers are used by heartbeat and network code.
- Configfs dependency helpers protect node/region items from removal while active.

## Risks
The structs are shared across cluster code, so lock discipline around `cl_nodes_lock` and configfs item references is essential.
