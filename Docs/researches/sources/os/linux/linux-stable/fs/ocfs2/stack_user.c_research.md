# File Research: sources/os/linux/linux-stable/fs/ocfs2/stack_user.c

Implements the OCFS2 `"user"` cluster stack plugin, bridging OCFS2 cluster operations to the kernel `fs/dlm` lockspace and, for older userspace stacks, the `/dev/ocfs2_control` misc device protocol.

Key responsibilities:
- Exposes `/dev/ocfs2_control` with a simple text protocol: read supported protocol tag `T01`, write `T01`, then send `SETN` for local node, `SETV` for locking protocol, and `DOWN` for node-down recovery notification.
- Maintains live filesystem connections in `ocfs2_live_connection_list`, protected by `ocfs2_control_lock`, so userspace `DOWN` messages can find a mounted UUID and call `cc_recovery_handler`.
- Tracks daemon/configuration state through `ocfs2_control_opened`, `ocfs2_control_this_node`, and `running_proto`.
- Registers `ocfs2_user_plugin` with stack glue and implements `struct ocfs2_stack_operations`.

Important behavior:
- `ocfs2_control_open/read/write/release()` implement handshake state, exact-sized command parsing, private per-open configuration, and final close cleanup.
- If the valid control daemon exits while live controlled connections remain, `ocfs2_control_release()` logs a fatal condition and calls `emergency_restart()`.
- `user_dlm_lock()` and `user_dlm_unlock()` wrap `dlm_lock()`/`dlm_unlock()`, provide AST/BAST wrappers, attach LVB storage, and force `DLM_LKF_NODLCKWT`.
- `user_plock()` routes POSIX lock operations to `dlm_posix_*()` helpers.
- Protocol negotiation without `dlm_controld` uses a DLM `VERSION_LOCK` resource and its LVB: first mounter writes the max protocol under EX then downconverts to PR; later mounters read and validate the LVB.
- DLM lockspace callbacks call OCFS2 recovery for failed slots and update the local node id/slot when recovery completes.
- `user_cluster_connect()` creates an exclusive DLM lockspace, detects old `dlm_controld` behavior via `ops_rv == -EOPNOTSUPP`, attaches the live connection, negotiates protocol version, and waits for local node discovery when no control daemon is used.
- `user_cluster_disconnect()` releases the version lock, releases the DLM lockspace, and drops live-connection state.

Integration points:
- Implements the `"user"` stack selected by `stackglue.c`.
- Uses kernel DLM APIs, DLM plock APIs, lockspace callbacks, OCFS2 locking protocol callbacks, and userspace `ocfs2_hb_ctl`/`dlm_controld` conventions.

Risk areas:
- Control daemon lifetime is safety-critical; unexpected loss while mounted triggers emergency restart.
- The text protocol is strict about command size and ordering.
- Protocol-version LVB negotiation must remain compatible across all nodes.
- Live connection teardown must prevent userspace recovery messages from touching freed mount state.
