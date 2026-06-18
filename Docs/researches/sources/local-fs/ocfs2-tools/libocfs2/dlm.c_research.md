# File Research: sources/local-fs/ocfs2-tools/libocfs2/dlm.c

Purpose: bridges libocfs2 to userspace cluster, heartbeat, and DLM libraries.

Key responsibilities:
- Looks up all journal system inode block numbers for configured slots.
- Initializes and shuts down DLM participation for a filesystem service.
- Joins/leaves heartbeat groups via o2cb region descriptors.
- Locks the cluster by taking the superblock DLM lock and probing each journal inode metadata lock.
- Reads and writes cluster stack metadata in the superblock.
- Encodes and takes/releases superblock and metadata lock resources.

Important APIs:
- `ocfs2_lock_down_cluster()`, `ocfs2_release_cluster()`
- `ocfs2_fill_cluster_desc()`, `ocfs2_set_cluster_desc()`
- `ocfs2_initialize_dlm()`, `ocfs2_shutdown_dlm()`
- `ocfs2_super_lock()`, `ocfs2_super_unlock()`
- `ocfs2_meta_lock()`, `ocfs2_meta_unlock()`

Core invariants:
- Non-default cluster stacks require extended slot maps.
- Classic `o2cb` stack enables `OCFS2_FEATURE_INCOMPAT_CLUSTERINFO` and disables userspace stack incompat.
- Non-`o2cb` stack enables userspace-stack only when clusterinfo is not enabled.
- Lock names are generated through `ocfs2_encode_lockres()` using block number and inode generation.

Dependencies:
- Uses `o2cb_*` cluster/group APIs and `o2dlm_*` lock APIs.
- Uses `ocfs2_fill_heartbeat_desc()` from `heartbeat.c`.
- Uses system inode lookup and cached inode metadata lock helpers.

Notable behavior:
- `ocfs2_initialize_dlm()` chooses `/dlm/` when stackglue is supported or the stack is classic/default; otherwise it passes `NULL` to avoid dlmfs.
- `ocfs2_fill_cluster_desc()` allocates `c_stack` and `c_cluster`; ownership is handed to the caller, but this file does not free them after initialization/shutdown paths.
- `ocfs2_lock_down_cluster()` unlocks the super lock on journal-lock failure, but journal locks are only try-lock probes and are immediately unlocked.
