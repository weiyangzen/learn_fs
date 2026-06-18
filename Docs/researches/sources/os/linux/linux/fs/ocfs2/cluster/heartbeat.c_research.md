# File Research: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.c

OCFS2 disk heartbeat implementation. It maintains heartbeat regions, writes this node’s heartbeat block, reads peer slots, generates node up/down callbacks, manages local/global heartbeat modes, and triggers self-fencing on write timeout/quorum failure.

Global state:
- Live-node state: `o2hb_live_slots[]`, `o2hb_live_node_bitmap`, node event queue, and callback semaphore.
- Global heartbeat region bitmaps: configured, live, quorum, and failed regions.
- Heartbeat mode: local or global; can only change before regions exist.
- Dependent users pin heartbeat regions to prevent configfs removal while DLM/user dependencies exist.

Region model:
- `struct o2hb_region` is a configfs item and owns one heartbeat thread, block-device file, slot pages, per-slot state, debugfs files, timeout work, negotiation work, live-node bitmap, and message handlers.
- `struct o2hb_disk_slot` tracks per-node raw slot data, last sequence/generation, live-list membership, and sample counters.

Heartbeat loop:
- `o2hb_thread()` depends the local node, repeatedly runs `o2hb_do_disk_heartbeat()`, sleeps so writes occur at the configured interval, and on clean stop writes generation zero as explicit down notification.
- `o2hb_do_disk_heartbeat()` reads configured/live peer slots, checks own slot integrity, prepares this node’s block, submits this node’s write, evaluates peer slots, waits for write completion, and arms timeout monitoring after steady state.
- Slot liveness requires `O2HB_LIVE_THRESHOLD` changed samples to become live and `o2hb_dead_threshold` equal samples or generation change to become dead.
- CRC protects each heartbeat block; bad CRC from a live node is treated as a transient miss.

Timeout and fencing:
- `o2hb_write_timeout()` logs heartbeat write timeout and calls `o2quo_disk_timeout()` unless global-heartbeat failed-region count is still below half of quorum regions.
- Negotiation work handles the case where all nodes may be stuck on a region; the lowest live node acts as master and can approve timeout extension/rearming.
- `o2hb_arm_timeout()` schedules write timeout and negotiation timeout only after steady state.

Configfs:
- The heartbeat group creates region items.
- Region attributes: `block_bytes`, `start_block`, `blocks`, `dev`, and read-only `pid`.
- Writing `dev` is the commit point: opens the block device, validates sector size and configured params, allocates slot pages, populates baseline data, starts the heartbeat thread, waits for steady state, and marks the region live in global mode.
- Heartbeat group attributes: `dead_threshold` and `mode`.
- Dropping a region stops its thread, clears global bitmaps, wakes pending start, and adjusts pinning.

Callbacks:
- `o2hb_setup_callback()`, `o2hb_register_callback()`, and `o2hb_unregister_callback()` provide priority-ordered node up/down callbacks.
- Callback execution is serialized by `o2hb_callback_sem`.
- `o2hb_fill_node_map()` gives callers a live-node snapshot serialized against callback changes.

Global/local heartbeat:
- Local mode pins only the region matching a domain/region UUID.
- Global mode assigns region numbers, tracks quorum regions, pins all active regions when dependent users exist and quorum-region count is small, and can unpin when enough quorum regions exist.

Debug:
- Optional debugfs directory `o2hb` exposes global live nodes, live regions, quorum regions, failed regions, plus per-region live nodes, region number, elapsed timeout time, and pinned state.

Exported interfaces:
- `o2hb_fill_node_map`, callback setup/register/unregister, heartbeat checks, stop-all-regions, get-all-regions, and global heartbeat mode query.
