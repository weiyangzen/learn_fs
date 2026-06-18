# File Research: sources/os/linux/linux/fs/ocfs2/cluster/nodemanager.h

Internal nodemanager header.

Defines:
- Fence methods: reset and panic.
- `struct o2nm_node`: configfs item, name, node number, one IPv4 address/port, rb-tree node, local flag, attribute-set bitmap, and lock.
- `struct o2nm_cluster`: configfs group, local-node state, node lock, node array, IP rb-tree, O2Net timeout settings, fence method, and configured-node bitmap.

Declares:
- Singleton cluster pointer.
- Local-node query, configured-node bitmap copy, node lookup by number/IP, node get/put.
- Configfs dependency helpers used by heartbeat to pin nodes/regions.
