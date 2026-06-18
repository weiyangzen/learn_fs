# File Research: sources/os/linux/linux/fs/ocfs2/cluster/quorum.c

OCFS2 quorum and self-fencing logic. It decides whether this node must fence itself when heartbeat and network connectivity disagree.

State:
- `o2quo_state` tracks heartbeating nodes, connected nodes, nodes holding quorum decisions, pending decision state, and a work item.
- Protected by `qs_lock`.

Fencing:
- `o2quo_fence_self()` stops all heartbeat regions, then either panics or emergency-restarts depending on cluster fence method.
- `o2quo_disk_timeout()` fences immediately after heartbeat disk write timeout.

Decision logic:
- `o2quo_make_decision()` runs asynchronously when holds drain.
- If this node is not heartbeating or is the only heartbeating node, no fence occurs.
- Odd-sized heartbeat set: this node must be connected to majority.
- Even-sized heartbeat set: this node must be connected to at least half, and if exactly half, its connected partition must include the lowest-numbered active node.
- Failure logs an error and fences.

Hold protocol:
- Holds delay quorum decisions during transitions where heartbeat/network state has not converged.
- `o2quo_hb_up()` adds a heartbeating node and holds if not connected.
- `o2quo_hb_down()` removes heartbeat state and clears holds.
- `o2quo_conn_up()` adds network connectivity and holds if heartbeat is not yet seen.
- `o2quo_conn_err()` removes connectivity and holds if the peer still heartbeats.
- `o2quo_hb_still_up()` marks a pending decision and clears a connection-error hold.

Lifecycle:
- `o2quo_init()` initializes lock and work.
- `o2quo_exit()` flushes pending work.
