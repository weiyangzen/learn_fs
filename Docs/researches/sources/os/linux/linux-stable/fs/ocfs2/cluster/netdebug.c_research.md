# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/netdebug.c

## Summary
Implements debugfs reporting for O2NET socket containers, active send tracking, connection statistics, and connected-node bitmaps when `CONFIG_DEBUG_FS` is enabled.

## Main Responsibilities
- Maintain debug-only lists of active `o2net_send_tracking` and `o2net_sock_container` objects.
- Provide seq_file iteration over active sends and sockets using dummy cursor objects.
- Report send wait timings, task identity, node, message id/type/key, and socket container pointers.
- Report socket connection details, krefs, endpoints, remote node, message handling state, and timing fields.
- Report compact CSV-style stats when `CONFIG_OCFS2_FS_STATS` is enabled.
- Expose connected-node bitmap through a simple debugfs file.
- Create/remove the `o2net` debugfs directory and files.

## Key Interfaces
- `o2net_debug_add_nst()` / `_del_nst()` track in-flight sends.
- `o2net_debug_add_sc()` / `_del_sc()` track socket containers.
- `o2net_debugfs_init()` creates `send_tracking`, `sock_containers`, `stats`, and `connected_nodes`.
- `o2net_debugfs_exit()` removes the tree.

## State and Synchronization
Uses `o2net_debug_lock` with bottom halves disabled around debug lists and seq iteration. Snapshot buffers for connected nodes are allocated at file open.

## Risks
This is diagnostic-only but reads live network structures under a debug spinlock. Output formats are consumed by tools such as `debugfs.ocfs2`, so field order and stats string version matter.
