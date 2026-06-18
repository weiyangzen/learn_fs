# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbutils.c

Small runtime-state helpers for `o2cb`.

`is_cluster_registered()` considers a cluster registered only if `o2cb_list_nodes()` finds a node marked local. `is_heartbeat_active()` returns true when `o2cb_list_hb_regions()` reports at least one active heartbeat region.
