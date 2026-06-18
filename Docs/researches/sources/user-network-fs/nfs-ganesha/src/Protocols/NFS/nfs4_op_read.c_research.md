# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_read.c

## Purpose
Implements NFSv4 READ, NFSv4.2 READ_PLUS, IO_ADVISE, and SEEK handling inside compound execution. It validates current file handles and stateids, routes pNFS data-server handles directly to DS operations, enforces export read size/offset limits, manages asynchronous FSAL read completion, maps FSAL results into NFS status, and records server I/O statistics.

## Important APIs, Types, and Functions
- `struct nfs4_read_data` is the heap continuation for async reads. It stores the response, optional owner reference, compound data, object handle, async flags, QoS flag, READ_PLUS `io_info`, and embedded `fsal_io_arg`.
- `nfs4_op_read`, `nfs4_op_read_plus`, `nfs4_op_io_advise`, and `nfs4_op_seek` are exported operation handlers.
- `nfs4_read` is the shared READ/READ_PLUS implementation. It calls `nfs4_sanity_check_FH`, `nfs4_Check_Stateid`, `allow_read`, `check_resp_room`, `fsal_read2`, and the FSAL `read2` object op.
- `nfs4_complete_read` finalizes EOF, result length, iovec ownership, statistics, owner/clientid cleanup, and state reference release.
- `op_dsread` and `op_dsread_plus` call `op_ctx->ctx_pnfs_ds->s_ops.dsh_read` or `dsh_read_plus` for pNFS data-server file handles.
- `nfs4_op_read_resume` and `nfs4_op_read_plus_resume` finish async, QoS, and FSAL-resume continuations from `data->op_data`.
- `xdr_READ4res_uio_release` releases read UIO buffers unless RDMA response buffers are in use.

## Control Flow
READ first sets `resp->resop`, detects minorversion data-server handles, and otherwise enters `nfs4_read`. The shared path checks that CurrentFH is a regular file, validates the input stateid, resolves open state from share/lock/delegation state, checks open mode and owner confirmation, handles anonymous special stateids and delegation conflicts, applies pre-read access policy, clamps against `MaxRead` and `MaxOffsetRead`, reserves response room, initializes the response iovec, allocates `nfs4_read_data`, optionally schedules QoS, and calls `fsal_read2`. If the callback completes before exit, the function completes inline; otherwise it returns `NFS_REQ_ASYNC_WAIT` and resume functions complete later.

READ_PLUS uses the same read path with an `io_info` pointer. On success `nfs4_complete_read_plus` overlays READ result state onto the READ_PLUS union and fills either `NFS4_CONTENT_HOLE` or `NFS4_CONTENT_DATA`. IO_ADVISE is NFSv4.2-only, validates a stateid, calls `obj_ops->io_advise`, and persists hints in `state_found->state_data.io_advise`. SEEK is also NFSv4.2-only and calls `obj_ops->seek2` with data/hole/adbs content selection.

## State and Persistence Behavior
The file touches transient compound state (`data->op_data`, `op_resp_size`, `current_obj`), NFS state refs, owner refs, and `op_ctx->clientid` for v4.0 owner-scoped I/O. State references are intentionally held through async callbacks and released in completion. IO_ADVISE stores hint bits on the open state for later read/seek operations. There is no durable storage update, but reads affect server statistics and QoS accounting.

## Dependencies and Integration Points
Depends on FSAL object operations (`read2`, `getattrs`, `test_access`, `io_advise`, `seek2`), SAL state management, pNFS DS callbacks, export limits and access policy, QoS (`qos_process`, `nfs4_qos_read_cb`), RDMA-aware response buffers, XDR UIO release, and LTTng tracepoints. The compound engine must invoke the matching resume handlers while `data->op_data` is live.

## Risks
- Async flag races around `ASYNC_PROC_DONE` and `ASYNC_PROC_EXIT` must preserve exactly one completion/free path.
- READ_PLUS uses union overlay behavior with READ results; changes to XDR unions or response structs could break `nfs4_complete_read_plus`.
- Zero-length, max-offset, and maxread clamping paths must leave response iovec and release callbacks in a valid state.
- pNFS DS READ_PLUS uses a directly allocated buffer and relies on FSAL-provided `io_info` fields; ownership must match free logic.
- EOF correction may call `getattrs` on completion; failure silently leaves FSAL EOF semantics in place.

## Test Signals
Exercise regular READ, zero-length READ, offset beyond `MaxOffsetRead`, size clamping, all-zero/all-one stateids, share-deny conflicts, delegation conflicts, v4.0 owner-confirmation failures, async FSAL completion before and after handler exit, FSAL `fsal_resume`, QoS delay and rate-control paths, pNFS DS reads, RDMA response-buffer cleanup, READ_PLUS data/hole responses, IO_ADVISE persistence, and SEEK for data/hole/not-supported cases.
