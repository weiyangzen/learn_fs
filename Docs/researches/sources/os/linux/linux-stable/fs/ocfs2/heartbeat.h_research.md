# File Research: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.h

Purpose: Declares OCFS2 heartbeat/node-map initialization, node-down handling, and bitmap helper APIs.

Read coverage: complete file read, 29 lines.

Key contents:
- `ocfs2_init_node_maps()` for mount-time node-map setup.
- `ocfs2_do_node_down()` callback for cluster node failure.
- Node-map set, clear, and test helpers used to track mounted or in-recovery nodes.

Dependencies:
- Consumed by DLM/cluster connection setup and recovery code.

Risk notes:
- Header exposes low-level node-map mutation helpers; callers are responsible for using the correct `ocfs2_node_map` and node number semantics.
