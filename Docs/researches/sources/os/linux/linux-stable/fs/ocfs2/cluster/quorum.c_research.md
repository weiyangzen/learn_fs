# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/quorum.c

## Summary
Implements O2CB quorum/fencing decisions based on heartbeat and network connectivity state. It fences the local node when it cannot reach a sufficient set of nodes that are still heartbeating.

## Main Responsibilities
- Track heartbeating nodes, connected nodes, and nodes in transitional hold states.
- Delay quorum decisions while heartbeat and connection state is racing.
- Decide whether the local node must fence itself after connection loss.
- Fence by stopping all heartbeat regions and either panicking or emergency restarting.
- React immediately to heartbeat disk write timeout.

## Key Interfaces
- `o2quo_hb_up()`, `o2quo_hb_down()`, and `o2quo_hb_still_up()` are called from heartbeat/network recovery logic.
- `o2quo_conn_up()` and `o2quo_conn_err()` track network connectivity.
- `o2quo_disk_timeout()` fences on local heartbeat write timeout.
- `o2quo_init()` and `o2quo_exit()` initialize/flush quorum work.

## Important Behavior
For odd-sized heartbeating sets, the node fences if it cannot connect to a majority. For even-sized sets, a half-quorum is only allowed if it includes the lowest-numbered live node; otherwise the node fences to break split brain.

Holds defer decisions while a node has started heartbeating but is not connected, or while a connection failed but heartbeat has not yet resolved whether the peer is really gone.

## State and Synchronization
Uses a single static `o2quo_state`, `spin_lock_bh()`, bitmaps for heartbeat/connection/hold state, a pending flag, and a work item for decisions outside event paths.

## Risks
This is intentionally heavy-handed and safety-critical. Incorrect hold accounting or bitmap transitions can cause premature self-fencing or failure to fence during split brain.
