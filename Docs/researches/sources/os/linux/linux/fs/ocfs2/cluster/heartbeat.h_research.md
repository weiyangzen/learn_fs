# File Research: sources/os/linux/linux/fs/ocfs2/cluster/heartbeat.h

Public cluster heartbeat header.

Defines:
- Heartbeat interval and thresholds: `O2HB_REGION_TIMEOUT_MS`, `O2HB_LIVE_THRESHOLD`, default/min dead threshold, and max write timeout expression.
- Region name length and callback magic.
- Callback types: node down and node up.
- `struct o2hb_callback_func` with list node, callback pointer, data, priority, type, and magic.

Declares:
- Heartbeat configfs group allocation/free.
- Callback setup/register/unregister APIs.
- Live-node map and node-heartbeating checks.
- Init/exit, stop-all-regions, get-all-regions, and global-heartbeat query.

Important dependency:
- Includes `ocfs2_heartbeat.h` for the on-disk heartbeat block layout.
