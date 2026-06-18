<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c

## Purpose
Implements NFSv4 `OP_DELEGRETURN`, returning a file delegation stateid to the server and deleting the corresponding delegation state on success.

## APIs, Types, and Functions
Exports `nfs4_op_delegreturn()` and `nfs4_op_delegreturn_Free()`. It uses `DELEGRETURN4args/res`, `nfs4_sanity_check_FH(REGULAR_FILE)`, `nfs4_Check_Stateid()`, `get_state_owner_ref()`, `deleg_heuristics_recall()`, `reset_cbgetattr_stats()`, `release_lease_lock()`, `nfs4_Errno_state()`, `state_del_locked()`, `STATELOCK_lock/unlock()`, and state refcount helpers.

## Control Flow, State, and Persistence
The handler validates the current FH as a regular file, converting `ISDIR` to `INVAL`, checks the delegation stateid, obtains the owner reference, locks the object state, updates delegation recall heuristics and CB_GETATTR stats, releases the owner ref, calls `release_lease_lock()` to return the delegation through SAL/FSAL, maps the state status, and deletes the delegation state if release succeeds. It unlocks the object and drops the state reference on exit. Persistent state changes include delegation removal, heuristics updates, and callback stat reset.

## Dependencies and Integration
Depends on NFSv4 stateid validation, delegation/lease SAL paths, object state locking, and FSAL lease release behavior. The compound dispatcher requires metadata-read export permission before calling it.

## Risks and Test Signals
Risks include stale owner/state handling, lock ordering around object state, deleting state after partial release failures, and protocol status differences for non-regular file handles. Test signals are successful delegation return, stale/bad stateid, directory handle returning `INVAL`, concurrent recall/return races, lease-release failure mapping, and state table cleanup verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c -->
