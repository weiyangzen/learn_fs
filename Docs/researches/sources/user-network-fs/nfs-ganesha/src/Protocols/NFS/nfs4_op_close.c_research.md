<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c

## Purpose
Implements NFSv4 `OP_CLOSE`, retiring an open stateid, cleaning related lock states, handling NFSv4.0 seqid replay behavior, and returning a final/invalid stateid.

## APIs, Types, and Functions
Exports `nfs4_op_close()`, `cleanup_layouts()`, `nfs4_op_close_Free()`, and `nfs4_op_close_CopyRes()`. It uses `CLOSE4args/res`, `nfs4_sanity_check_FH()`, `nfs4_check_stateid_acquire_state_lock()`, `Check_nfs4_seqid_locked()`, `state_unlock_all_locked()`, `state_del_locked()`, `update_stateid_locked()`, `Copy_nfs4_state_req()`, `nfs4_return_one_state()`, and state/object owner reference helpers.

## Control Flow, State, and Persistence
The handler validates a regular-file current FH, checks and locks the open state, treats certain v4.0 races as replayed close success, validates v4.0 owner seqid, deletes all associated lock states, returns an incremented stateid for v4.0 or an all-zero/`UINT32_MAX` invalid stateid for v4.1+, deletes the open state, invalidates `current_stateid`, and for v4.1+ calls `cleanup_layouts()` to return pNFS layouts marked return-on-close when this was the last open. It releases state locks, object refs, owner refs, and state refs on exit.

## Dependencies and Integration
Deeply integrated with SAL state management, open-owner replay cache, pNFS layout state, FSAL extended close effects via state deletion, and compound current-object state. The dispatcher uses the free/copy hooks for replay cache support.

## Risks and Test Signals
Risks include state lock/ref leaks, close replay ambiguity, deleting locks while iterating, layout return-on-close races, invalid stateid semantics across minor versions, and stale state objects after concurrent closes. Test signals are v4.0 seqid replay and misorder tests, v4.1 close invalid stateid, lock cleanup, last-close layout return, concurrent close/open tests, and sanitizer checks around state reference paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c -->
