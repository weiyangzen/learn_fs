# File Research: sources/os/linux/linux/fs/afs/rotate.c

## Scope

This file implements fileserver selection, address rotation, retry policy, and diagnostic dumping for AFS/YFS file-server operations.

## Public And Internal APIs Covered

- `afs_clear_server_states()` releases per-operation endpoint-state references.
- `afs_select_fileserver()` is the main iterator used by operation execution to choose the next server/address or stop with a final error.
- `afs_dump_edestaddrreq()` emits debug state for address-selection failures when cursor debugging is enabled.

## Control Flow And Behavior

- Iteration starts by taking the volume server list, allocating one `afs_server_state` per server, snapshotting endpoint state/probe sequence/address mask, and preferring the vnode callback server when possible.
- If a vnode has an outstanding server affinity but that server no longer serves the volume, callbacks are cleared. `AFS_OPERATION_CUR_ONLY` instead fails with `-ESTALE`.
- Successful calls update volume state through `afs_update_volume_state()` and may restart if RO volume replication state requires retrying from the beginning.
- Fileserver aborts are translated carefully: `VNOVOL` refreshes VLDB state, `VMOVED` triggers volume update and restart, busy/offline errors mark per-server volume state and may sleep, quota/full errors map to local `-EDQUOT`/`-ENOSPC`, and unsupported opcodes can drive downgrade retry.
- Network failures rotate addresses first, then servers. Probe state determines responsive addresses and server eligibility.
- Address choice uses address preference priority and records `last_error` on failed addresses.
- When all servers are exhausted, accumulated endpoint/probe errors are folded into the operation result; busy volumes may sleep and restart.

## State And Data Structures

- Operates on `struct afs_operation` fields including `server_list`, `server_states`, `untried_servers`, `server_index`, `estate`, `addr_tried`, `addr_index`, `flags`, and cumulative error state.
- Uses per-server flags such as `AFS_SE_VOLUME_BUSY`, `AFS_SE_VOLUME_OFFLINE`, and `AFS_SE_EXCLUDED`.
- Updates vnode callback server affinity and callback promise state under `cb_lock`.

## Dependencies

- Relies on volume status refresh in `afs_check_volume_status()`, server record checking in `afs_check_server_record()`, fileserver probing helpers, address-preference helpers, and callback invalidation helpers.
- Uses RxRPC peer addresses for diagnostics.

## Risks And Invariants

- Server and address bitmasks assume the list sizes fit in an unsigned long bitset.
- `CUR_ONLY` operations, especially lock-related ones, must not silently move to another server.
- Callback promises are cleared when server affinity changes to avoid trusting stale validity state.
- Volume busy/offline sleeps must respect interruptible versus uninterruptible operation flags.
