# File Research: sources/local-fs/dlm/dlm_sand/main.c

## Purpose
Implements `dlm_sand`, an experimental DLM/GFS2 event-log coordinator backed by shared storage and sanlock. It initializes/dumps an events LV, watches DLM kernel uevents for lockspace online/offline transitions, coordinates cluster membership changes through an on-disk log, and drives kernel DLM configfs/sysfs start/stop actions.

## Main Responsibilities
- Provides `dlm_sand init /dev/vg/lv_events` to format a 512 MiB events LV with header, node, summary, record, and sanlock lease areas.
- Provides `dlm_sand dump /dev/vg/lv_events` to inspect the event header, node table, summary, and event records.
- Runs a daemon that listens for kernel DLM uevents and client commands over abstract UNIX sockets.
- Tracks per-GFS2/DLM lockspaces derived from `vg-lv` names and per-VG sanlock lockspaces named `lvm_<vg>`.
- Maintains membership recovery using on-disk records: `EV_JOIN`, `EV_LEAVE`, `EV_FAILED`, `EV_FENCED`, `EV_STOPPED`, `EV_STARTED`.
- Uses sanlock host state as the source of failed/fenced generation changes.
- Exposes status, config, and debug dumps for `dlm_tool`.

## Key Flows
- Startup reads CLI/config defaults, determines local node id from `/etc/lvm/lvmlocal.conf` or `dlm.conf`, validates `local_ipaddr`, daemonizes unless foreground/debug, locks `/run/dlm_sand.pid`, initializes configfs/local node, starts query sockets, and polls uevents.
- Online uevent creates a `lockspace`, finds/adds its VG sanlock lockspace, records local generation, starts a `lockspace_thread`.
- `lockspace_thread` opens the events LV, validates the header, initializes node metadata, finds the end of the log from the summary record, waits for a safe join point, writes a join, starts the kernel lockspace, and then continually processes log records and sanlock failure state.
- Offline uevent sets `ls->leave`, waits for the lockspace thread to write leave/stop records, tears down configfs state, closes descriptors, and drops unused VG state.
- Query thread serializes status/debug/config responses with `query_mutex` so `copy_status()` can inspect shared lists safely.

## Important Data/Interfaces
- Depends on `sand_internal.h` structures such as `lockspace`, `current_event`, `dlm_node`, and `vg_lockspace`.
- Uses `ondisk.c` helpers for little-endian header/node/summary/record serialization.
- Uses sanlock APIs: `sanlock_inq_lockspace`, `sanlock_get_hosts`, `sanlock_acquire`, `sanlock_release`, `sanlock_read_resource`, `sanlock_direct_write_resource`.
- Uses action/config helpers declared in `sand_internal.h` for configfs/sysfs work.
- Uses abstract UNIX sockets from `dlm_sand_sock.h`.

## Notable Implementation Details
- The event log is circular; record number modulo `record_count` chooses the physical record index, while `wraps` tracks wraps.
- `last_all_started_rn` summary is an optimization so joining nodes do not scan from the beginning.
- Joining is deliberately restricted to stable points: after all-started, after last-leave, after compatible join, or after log reset if old members are dead/free.
- Failure handling writes failed/fenced records only after filtering notices already seen from other nodes.
- `cur_event_status` mirrors the active recovery state for `dlm_tool status`.

## Risks / Gaps
- Several error branches contain empty blocks after failed allocation/read/write calls, so some failures are logged weakly or continue unsafely.
- `client_alloc()` may leak the old `client` array if `realloc(client)` succeeds and `realloc(pollfd)` fails.
- Many fixed-size string copies assume prior length constraints; most are bounded by naming rules, but enforcement is uneven.
- `process_uevent()` frees `vg` directly in one error path even when `get_add_vg_lockspace()` may have linked or initialized state; this path needs careful audit.
- The daemon ignores shutdown while active lockspaces exist, which is intentional, but operationally means service stop can hang until unmount/offline completes.
