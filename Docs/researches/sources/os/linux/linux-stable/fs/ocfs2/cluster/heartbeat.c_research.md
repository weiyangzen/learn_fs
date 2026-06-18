# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.c

## Summary
Implements O2CB disk heartbeat. It manages heartbeat configfs regions, per-region heartbeat kthreads, bio-based slot reads/writes, CRC-protected on-disk heartbeat blocks, live-node detection, node up/down callbacks, global heartbeat region/quorum tracking, write timeout fencing, timeout negotiation messages, debugfs reporting, and callback registration.

## Main Responsibilities
- Maintain global live-node, live-region, quorum-region, and failed-region bitmaps.
- Create and destroy heartbeat regions under the cluster configfs hierarchy.
- Open heartbeat block devices, map slot pages, seed slot state, and start/stop heartbeat kthreads.
- Periodically read configured node slots, write the local node slot, verify CRCs, and detect membership changes.
- Queue serialized node up/down callbacks for DLM, networking, and other cluster users.
- Detect stalled heartbeat writes and trigger quorum fencing when necessary.
- Support local and global heartbeat modes, including region pinning for dependent users.
- Expose heartbeat state through debugfs.

## Key Interfaces
- `o2hb_alloc_hb_set()` / `o2hb_free_hb_set()` provide the configfs heartbeat group.
- `o2hb_setup_callback()`, `o2hb_register_callback()`, and `o2hb_unregister_callback()` manage ordered callbacks.
- `o2hb_fill_node_map()` returns currently heartbeating nodes.
- `o2hb_check_node_heartbeating_*()` test node liveness in normal or callback contexts.
- `o2hb_stop_all_regions()`, `o2hb_get_all_regions()`, and `o2hb_global_heartbeat_active()` support cluster management.
- `o2hb_init()` / `o2hb_exit()` initialize global structures and debugfs.

## Important Behavior
A region becomes active when userspace writes a block-device fd to its `dev` configfs attribute after setting block size, start block, and slot count. The region opens the block device, maps one heartbeat slot per node, starts an `o2hb-*` thread, and waits until the thread reaches a steady state.

Each heartbeat pass reads configured slots, verifies the local slot still matches the previous write, prepares a new local slot with sequence time, node number, generation, dead timeout, and CRC, writes it synchronously, checks every slot for live/dead transitions, and rearms write-timeout work only after a good own-slot check.

A dead node becomes live after `O2HB_LIVE_THRESHOLD` changed samples. A live node becomes dead after `o2hb_dead_threshold` equal samples or generation change. First live region entry for a node emits an up callback; last region exit emits a down callback.

Global heartbeat promotes a region to quorum only after it sees all globally live nodes. Failed quorum regions can trigger fencing when enough write timeouts occur.

## State and Synchronization
Uses `o2hb_live_lock`, `o2hb_callback_sem`, configfs item references, kthreads, delayed work, per-region handler lists, bio completions, bitmaps, and node references from nodemanager.

## Cross-File Interactions
Calls nodemanager for configured/local nodes and configfs dependencies, tcp for timeout negotiation messages, quorum for disk timeout fencing, and masklog/debugfs for observability.

## Risks
Heartbeat is safety-critical. Bugs in slot ownership checks, CRC handling, steady-state waits, timeout arming, generation changes, global quorum accounting, or callback serialization can cause false node death, missed fencing, or unsafe concurrent filesystem access.
