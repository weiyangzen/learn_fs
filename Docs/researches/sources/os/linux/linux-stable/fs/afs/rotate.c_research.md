# File Research: sources/os/linux/linux-stable/fs/afs/rotate.c

## Scope

Implements fileserver selection and retry rotation for AFS operations across volume server lists and endpoint address lists.

## APIs And Behavior

- `afs_clear_server_states()` releases per-operation endpoint-state references.
- `afs_select_fileserver()` drives the operation cursor: refreshes volume status, starts server iteration, waits for probes, picks a responding server/address by priority, handles abort/error outcomes, and decides whether to retry, switch server, refresh VLDB state, or fail.
- Handles special volume aborts including `VNOVOL`, `VMOVED`, `VBUSY`, `VOFFLINE`, quota/full errors, opcode downgrade, old OpenAFS timeout aliases, and UAE errors.
- `afs_dump_edestaddrreq()` emits limited debug state for destination-address failures.

## State And Dependencies

The rotation cursor mutates `struct afs_operation` fields such as `server_list`, `server_states`, `server_index`, `addr_index`, `addr_tried`, cumulative error, callback server, and VolSync state. It depends on volume status refresh, fileserver probes, server record validation, endpoint address preferences, callback promise clearing, and AFS/YFS RPC operation dispatch.

## Risks And Invariants

The code preserves callback/lock affinity when `AFS_OPERATION_CUR_ONLY` is set and treats server-list changes as restart points. RO replication cutover is guarded through `afs_update_volume_state()`. Error prioritization and retry flags prevent infinite VMOVED/VNOVOL loops while still allowing busy/offline volumes to recover.
