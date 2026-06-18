# File Research: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.c

Purpose: Maintains OCFS2 node maps and handles cluster node-down notifications by starting recovery.

Read coverage: complete file read, 101 lines.

Key structures and state:
- Operates on `struct ocfs2_node_map`, using a fixed maximum node count and bitmap storage.
- Initializes and protects mount node maps with `osb->node_map_lock`.
- Currently initializes the recovering-orphan-directories node map.

Major logic:
- `ocfs2_init_node_maps()` initializes the node-map spinlock and the orphan recovery node map.
- `ocfs2_do_node_down()` ignores notifications before cluster connection setup, rejects self-death notifications, and starts `ocfs2_recovery_thread()` for the dead node.
- Node-map helpers set, clear, and test bits under `node_map_lock`.
- Set/clear helpers special-case `-1` and return without action.

Concurrency and lifetime:
- Node-map bitmap operations are protected by `node_map_lock`.
- Node-down recovery depends on `osb->cconn` being established; early notifications are intentionally ignored because slot checking later catches them.

Important dependencies:
- Uses Linux bitmap helpers, OCFS2 recovery thread logic, superblock state, and tracepoints.

Risk notes:
- Test-bit with an out-of-range node logs and BUGs; callers must validate node numbers except for the set/clear `-1` special case.
- Ignoring node-down before `cconn` exists assumes later mount/slot recovery will observe the death.
