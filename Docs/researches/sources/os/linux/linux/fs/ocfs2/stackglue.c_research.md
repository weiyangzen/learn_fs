# File Research: sources/os/linux/linux/fs/ocfs2/stackglue.c

## Purpose

`stackglue.c` is the OCFS2 cluster stack abstraction layer. It lets the filesystem mount path request either the classic `o2cb` stack or the generic userspace stack, pins the chosen stack module while active, forwards lock operations to the selected plugin, and exposes OCFS2 cluster-stack status/configuration through sysfs and sysctl.

## Major State

- `locking_max_version`: global maximum OCFS2 locking protocol version set by `ocfs2_stack_glue_set_max_proto_version()`.
- `ocfs2_stack_list`: registered stack plugins.
- `cluster_stack_name`: selected stack label, defaulting to `o2cb`.
- `active_stack`: currently selected plugin while one or more cluster connections are active.
- `ocfs2_hb_ctl_path`: helper path for `ocfs2_hb_ctl`, exposed through `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.
- `ocfs2_stack_lock`: spinlock protecting plugin list, active stack, stack count, and stack-name configuration.

## Stack Selection

`ocfs2_stack_driver_get()` normalizes stack selection:

- Empty or missing stack name means classic `o2cb`.
- Stack names must be exactly `OCFS2_STACK_LABEL_LEN`.
- Anything other than `o2cb` selects plugin `user`.
- If the plugin is absent, it requests `ocfs2_stack_<plugin_name>` and retries.
- It refuses to switch stacks while another active stack is pinned.

`ocfs2_stack_driver_request()` performs the protected lookup:

- Rejects a requested stack label that differs from `cluster_stack_name`.
- If `active_stack` already exists, only the same plugin can be reused.
- Otherwise, looks up the plugin, pins its module owner, sets `active_stack`, and increments `sp_count`.

`ocfs2_stack_driver_put()` decrements the active plugin reference count and drops the module reference when the count reaches zero.

## Plugin Registration

- `ocfs2_stack_glue_register()` adds a unique plugin by name, initializes its `sp_count`, copies the current max protocol, and logs registration.
- `ocfs2_stack_glue_unregister()` verifies the plugin is registered, not active, and not referenced before removing it.
- `ocfs2_stack_glue_set_max_proto_version()` sets the global max protocol once and propagates it to all already-registered plugins.

## Exported Cluster API

The filesystem-facing functions are thin wrappers around the active stack:

- `ocfs2_cluster_connect()` allocates `struct ocfs2_cluster_connection`, fills group/cluster names, protocol callbacks, recovery callback, and starting version, pins/selects the stack, then calls plugin `connect`.
- `ocfs2_cluster_connect_agnostic()` uses the configured global `cluster_stack_name` if set.
- `ocfs2_cluster_disconnect()` calls plugin `disconnect`, frees the connection, and optionally drops the stack reference depending on `hangup_pending`.
- `ocfs2_cluster_hangup()` runs `ocfs2_hb_ctl -K -u <group>` and drops the deferred stack reference.
- `ocfs2_cluster_this_node()` forwards local-node lookup to the active plugin.

DLM wrappers:

- `ocfs2_dlm_lock()` stores the connection pointer in the LKSb on first use and forwards lock requests.
- `ocfs2_dlm_unlock()`, `ocfs2_dlm_lock_status()`, `ocfs2_dlm_lvb_valid()`, `ocfs2_dlm_lvb()`, and `ocfs2_dlm_dump_lksb()` forward through `active_stack->sp_ops`.
- `ocfs2_stack_supports_plocks()` and `ocfs2_plock()` expose optional cluster-aware POSIX locks.

## Sysfs and Sysctl Surface

Creates `/sys/fs/ocfs2` via `ocfs2_kset` with attributes:

- `max_locking_protocol`: current max OCFS2 locking protocol.
- `loaded_cluster_plugins`: registered plugin names.
- `active_cluster_plugin`: active plugin name, if any.
- `cluster_stack`: selected cluster stack label; writable only when no active stack conflicts.
- `dlm_recover_callback_support`: constant `1`.

Registers sysctl path `/proc/sys/fs/ocfs2/nm/hb_ctl_path` to configure the helper path used during unmount hangup.

## Correctness Notes

- `active_stack` means both module pinning and locking protocol stability.
- Stack labels are fixed length to match on-disk OCFS2 cluster stack labels.
- `ocfs2_cluster_hangup()` is separate from `ocfs2_cluster_disconnect()` because ocfs2-tools expects heartbeat cleanup on unmount even in cases where DLM setup did not fully occur.
- The global `active_stack` model means mixed stack plugins cannot be used concurrently in one kernel instance.
