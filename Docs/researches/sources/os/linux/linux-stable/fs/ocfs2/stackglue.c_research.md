# File Research: sources/os/linux/linux-stable/fs/ocfs2/stackglue.c

Implements the OCFS2 cluster-stack glue layer. It selects one active cluster stack plugin, exposes generic OCFS2 cluster/DLM APIs to filesystem code, manages stack module pinning, and provides sysfs/sysctl controls for stack selection and heartbeat helper path.

Key responsibilities:
- Maintains registered stack plugins in `ocfs2_stack_list`, protected by `ocfs2_stack_lock`.
- Tracks the currently active plugin in `active_stack`; only one stack can be active while mounts exist.
- Chooses the `"o2cb"` plugin for the classic stack label and `"user"` for any non-classic stack label.
- Auto-loads `ocfs2_stack_<plugin>` modules on demand.
- Registers `/sys/fs/ocfs2` attributes and `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.

Important exported APIs:
- Plugin lifecycle: `ocfs2_stack_glue_register()`, `ocfs2_stack_glue_unregister()`.
- Protocol setup: `ocfs2_stack_glue_set_max_proto_version()`.
- DLM wrappers: `ocfs2_dlm_lock()`, `ocfs2_dlm_unlock()`, `ocfs2_dlm_lock_status()`, `ocfs2_dlm_lvb_valid()`, `ocfs2_dlm_lvb()`, `ocfs2_dlm_dump_lksb()`.
- Cluster connection: `ocfs2_cluster_connect()`, `ocfs2_cluster_connect_agnostic()`, `ocfs2_cluster_disconnect()`, `ocfs2_cluster_hangup()`, `ocfs2_cluster_this_node()`.
- POSIX locks: `ocfs2_stack_supports_plocks()`, `ocfs2_plock()`.

Important behavior:
- `ocfs2_cluster_connect()` validates group length and locking protocol max version, allocates `ocfs2_cluster_connection`, pins/selects the stack, and calls plugin `connect`.
- `ocfs2_cluster_disconnect()` calls plugin `disconnect`, frees the connection, and drops the stack module reference unless a later heartbeat hangup is pending.
- `ocfs2_cluster_hangup()` runs the configured userspace helper with `-K -u <uuid>` and then drops the pending stack reference.
- Sysfs exposes `max_locking_protocol`, loaded plugins, active plugin, selected cluster stack label, and DLM recovery callback support.
- The `cluster_stack` sysfs attribute can be changed only when no active stack is mounted.

Integration points:
- Filesystem mount code calls this layer through `dlmglue.c`/mount paths.
- Stack plugins such as `stack_user.c` and the classic O2CB stack register here.
- `super.c` uses exported `ocfs2_kset` for per-device sysfs directories.

Risk areas:
- Active stack and module references must stay synchronized with mount/disconnect/hangup sequencing.
- The selected stack label is global while active, so mixed-stack mounts are intentionally rejected.
- `ocfs2_dlm_dump_lksb()` assumes the active stack provides the debugging hook.
