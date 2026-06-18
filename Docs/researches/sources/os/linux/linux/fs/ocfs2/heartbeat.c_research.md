# File Research: sources/os/linux/linux/fs/ocfs2/heartbeat.c

OCFS2 heartbeat callback and node-map helper implementation. This is a small bridge between cluster heartbeat/node-down notification and OCFS2 recovery bookkeeping.

Node maps:
- `ocfs2_node_map_init()` initializes maps with `OCFS2_NODE_MAP_MAX_NODES` and clears all bits.
- `ocfs2_init_node_maps()` initializes the superblock node-map spinlock and the recovering orphan-directory map.
- `ocfs2_node_map_set_bit()`, `ocfs2_node_map_clear_bit()`, and `ocfs2_node_map_test_bit()` update/test maps under `osb->node_map_lock`.
- Bit `-1` is silently ignored for set/clear as a special legacy case.
- Out-of-range positive bits trigger `BUG_ON()` or explicit error logging and BUG.

Node-down handling:
- `ocfs2_do_node_down()` is the cluster-stack node-down callback registered during DLM connect.
- It asserts the local node is not reported down.
- If the cluster connection is not yet established, it ignores the event because slot scanning after connect will notice recovery needs.
- Otherwise it calls `ocfs2_recovery_thread(osb, node_num)` to start recovery for the dead node.

Dependencies:
- Recovery and journal code receive node-down events.
- Node maps are used to track mounted/recovering node state such as orphan directory recovery.

Important invariants:
- Node map operations require the superblock’s node-map lock.
- Heartbeat callback can arrive before full cluster setup; the file explicitly treats that as safe to ignore.
