# File Research: sources/os/linux/linux/fs/ocfs2/stackglue.h

## Purpose

`stackglue.h` defines the public OCFS2 cluster stack abstraction used by filesystem code and implemented by stack plugins such as `o2cb` and `user`. It hides stack-specific DLM lock status structures behind `struct ocfs2_dlm_lksb`, defines the connection and callback contracts, and declares exported stack glue functions.

## Key Types

- `struct ocfs2_protocol_version`:
  - Two-byte major/minor locking protocol version for inter-node OCFS2 behavior.
- `struct fsdlm_lksb_plus_lvb`:
  - Combines an `fs/dlm` `struct dlm_lksb` with inline LVB storage so the union has enough room.
- `struct ocfs2_dlm_lksb`:
  - Union of the classic o2dlm lock status, fs/dlm lock status, and padding/LVB storage.
  - Includes `lksb_conn` so callbacks can verify and recover the owning cluster connection.
- `struct ocfs2_locking_protocol`:
  - Filesystem callback table supplied to stack plugins.
  - Contains max version and lock AST, blocking AST, and unlock AST callbacks.
- `struct ocfs2_cluster_connection`:
  - Opaque-to-filesystem connection record carrying group name, cluster name, negotiated version, recovery callback, lockspace pointer, and plugin private state.
- `struct ocfs2_stack_operations`:
  - Plugin operation table for connect/disconnect, local node lookup, DLM lock/unlock/status/LVB access, optional plocks, and optional lock-status dumping.
- `struct ocfs2_stack_plugin`:
  - Registration record containing plugin name, operation table, module owner, list node, reference count, and max protocol.

## Constants

- `DLM_LKF_LOCAL` is locally defined because the public DLM constants header lacks it.
- `GROUP_NAME_MAX` shadows the internal DLM lockspace-name length.
- `CLUSTER_NAME_MAX` shadows the OCFS2 cluster name length.

## API Surface

Filesystem-facing API:

- `ocfs2_cluster_connect()`
- `ocfs2_cluster_connect_agnostic()`
- `ocfs2_cluster_disconnect()`
- `ocfs2_cluster_hangup()`
- `ocfs2_cluster_this_node()`
- `ocfs2_dlm_lock()` / `ocfs2_dlm_unlock()`
- `ocfs2_dlm_lock_status()`
- `ocfs2_dlm_lvb_valid()`
- `ocfs2_dlm_lvb()`
- `ocfs2_dlm_dump_lksb()`
- `ocfs2_stack_supports_plocks()`
- `ocfs2_plock()`
- `ocfs2_stack_glue_set_max_proto_version()`

Plugin-facing API:

- `ocfs2_stack_glue_register()`
- `ocfs2_stack_glue_unregister()`

## Correctness Notes

- The stack `connect()` contract is strong: it must not return until node-down notifications and lock processing are guaranteed.
- The stack `disconnect()` contract requires no further references to the connection after return.
- AST arguments are intentionally not passed through the generic lock API; stack implementations wrap stack-specific callbacks and pass the `ocfs2_dlm_lksb` back to OCFS2.
- `plock` is optional and must be checked through `ocfs2_stack_supports_plocks()`.
