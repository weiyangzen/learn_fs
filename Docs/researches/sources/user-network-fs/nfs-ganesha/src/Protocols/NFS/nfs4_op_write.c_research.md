# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_write.c

## Purpose
Implements NFSv4 WRITE, pNFS data-server WRITE, unsupported WRITE_SAME, and QoS write callbacks. It validates filehandle/state/access/quota/limits, dispatches async FSAL writes, completes stable-write metadata and verifier fields, and records write statistics.

## Important APIs, Types, and Functions
- `struct nfs4_write_data` is the async continuation for writes.
- `nfs4_op_write`, `nfs4_op_write_resume`, `op_dswrite`, `nfs4_complete_write`, and `nfs4_write_cb` are the core write path.
- Uses `nfs4_Check_Stateid`, `state_deleg_conflict`, `check_quota`, `obj_ops->test_access`, `obj_ops->write2`, `get_write_verifier`, `server_stats_io_done`, QoS `qos_process`, and pNFS DS `dsh_write`.
- `nfs4_op_write_same` returns `NFS4ERR_NOTSUPP`.

## Control Flow
The handler traces and sets response op, routes v4.1+ DS handles to `op_dswrite`, checks CurrentFH regular-file sanity, checks quota, validates the input stateid, resolves share/lock/delegation state, enforces write open access or delegation write type, checks delegation conflicts for special stateids, tests FSAL write access, enforces `MaxOffsetWrite` and clamps `MaxWrite`, handles zero-length writes by returning FILE_SYNC and a write verifier, optionally sets v4.0 owner clientid, allocates `nfs4_write_data`, fills `fsal_io_arg`, runs QoS if enabled, and calls `write2`.

Async completion converts FSAL status, sets done flags, and resumes the request if needed. Completion sets committed mode based on `fsal_stable`, count from `io_amount`, write verifier from the export, stats, and releases owner/state refs. Resume handles QoS continuation, FSAL resume requests, completion, and freeing `data->op_data`.

## State and Persistence Behavior
Writes mutate file contents through FSAL or DS operations and may require stable storage depending on requested stability or export `EXPORT_OPTION_COMMIT`. The operation temporarily holds NFS state and owner refs across async execution and updates stats. It does not directly persist client state.

## Dependencies and Integration Points
Depends on FSAL object write APIs, pNFS DS write ops, SAL state/delegation logic, quota checks, export write limits and commit policy, QoS throttling, write-verifier generation, and compound async resume machinery.

## Risks
The expression `(offset + size) > MaxOffsetWrite` can overflow if offset is near `UINT64_MAX`; tests should cover boundary behavior. Async/QoS paths must free `write_data` exactly once. Stable/unstable commit semantics depend on FSAL setting `fsal_stable`. DS write path asserts a single iovec. Zero-length writes must still return a valid verifier.

## Test Signals
Test normal writes, zero-length writes, quota failure, access failure, share/openmode errors, delegation write/non-write stateids, special stateid delegation conflicts, max write clamping, max offset/fbig, async callback-before/after-exit, FSAL resume, QoS delay/rate paths, pNFS DS writes, forced sync export option, and WRITE_SAME not supported.
