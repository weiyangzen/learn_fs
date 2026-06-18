# File Research: sources/local-fs/ocfs2-tools/include/o2cb/o2cb.h

This is the public userspace API header for O2CB cluster configuration, heartbeat, and control operations.

Key content:
- Defines cluster stack names: `o2cb`, `pcmk`, and `cman`.
- Provides inline validators for stack names, cluster names, classic O2CB alphanumeric cluster names, and heartbeat modes.
- Declares initialization, cluster create/remove/list, node add/delete/list/query, heartbeat region list/query, heartbeat mode, and daemon debug APIs.
- Defines `o2cb_cluster_desc` and `o2cb_region_desc`.
- Declares heartbeat lifecycle and group join/leave APIs.
- Declares region reference helpers and node property accessors.
- Declares control-daemon open/close, node-down notification, max locking protocol query, heartbeat control path lookup, and stack setup.

Integration notes:
- Includes generated `o2cb_err.h`, nodemanager/heartbeat public structs, and OCFS2 kernel filesystem definitions.
- Used by OCFS2 userspace tools that need cluster stack and heartbeat coordination.
