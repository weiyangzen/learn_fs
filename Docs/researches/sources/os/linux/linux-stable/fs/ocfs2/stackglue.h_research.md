# File Research: sources/os/linux/linux-stable/fs/ocfs2/stackglue.h

Defines the public OCFS2 cluster-stack abstraction shared by filesystem code and stack plugins.

Key contents:
- Defines stack-independent limits `GROUP_NAME_MAX` and `CLUSTER_NAME_MAX`.
- Defines `struct ocfs2_protocol_version`, the filesystem locking protocol version used for inter-node compatibility.
- Defines `struct ocfs2_dlm_lksb`, a union large enough for O2DLM and fs/dlm lock status blocks plus LVB storage.
- Defines `struct ocfs2_locking_protocol`, the callback table OCFS2 passes to stacks for lock AST, blocking AST, and unlock AST notifications.
- Defines `struct ocfs2_cluster_connection`, the per-mounted-filesystem connection object carrying group name, cluster name, negotiated version, callbacks, lockspace pointer, and stack-private data.
- Defines `struct ocfs2_stack_operations`, the plugin vtable for connect/disconnect, node identity, DLM lock/unlock/status/LVB access, optional POSIX locks, and optional lock dump support.
- Defines `struct ocfs2_stack_plugin`, the registration object used by stackglue.

Important API contracts:
- `connect()` must not return until recovery notifications and locking requests are ready.
- `disconnect()` must not return while the stack can still reference the connection.
- DLM wrappers do not pass explicit AST arguments; stacks call back through the connection protocol using the `ocfs2_dlm_lksb`.
- `plock` is optional and callers must check support.
- `DLM_LKF_LOCAL` is locally faked because the public DLM constants header lacks that flag.

Integration points:
- Included by OCFS2 DLM glue, mount logic, stack plugins, and user-stack code.
- Bridges classic O2CB lock status layout and kernel `fs/dlm` layout without exposing those internals to most filesystem code.

Risk areas:
- Lock status union layout must remain large enough for all supported stacks.
- Protocol max-version negotiation depends on all stacks seeing the same `sp_max_proto`.
- Stack callbacks define strict lifetime and notification semantics; violating them can leave mounted filesystems without cluster recovery or locking.
