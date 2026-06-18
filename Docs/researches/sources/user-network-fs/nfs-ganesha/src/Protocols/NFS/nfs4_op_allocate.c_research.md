<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c

## Purpose
Implements NFSv4.2 `OP_ALLOCATE` and `OP_DEALLOCATE`, changing file space allocation through the FSAL `fallocate` operation with NFSv4 stateid and permission checks.

## APIs, Types, and Functions
Exports `nfs4_op_allocate()` and `nfs4_op_deallocate()` with shared helper `allocate_deallocate()`. It uses `ALLOCATE4args`, `DEALLOCATE4args`, `stateid4`, `nfs4_sanity_check_FH()`, `nfs4_Check_Stateid()`, `nfs4_State_Get_Pointer()`, `state_deleg_conflict()`, `obj->obj_ops->test_access()`, `obj->obj_ops->fallocate()`, export `MaxOffsetWrite`, and `check_quota(FSAL_QUOTA_BLOCKS)`.

## Control Flow, State, and Persistence
The shared helper requires a regular-file current FH, checks block quota, validates the stateid, converts lock stateids to their open state, accepts write delegations for ordering, rejects invalid state types and opens without write access, checks anonymous stateids for delegation conflicts, verifies write access, enforces max write offset, treats zero length as no-op success, and calls `fallocate(obj, state, offset, size, allocate)`. It releases state references before returning. Persistent file allocation state changes only through FSAL `fallocate`.

## Dependencies and Integration
Depends on NFSv4 state management, delegation conflict rules, export write limits, quota implementation, and FSAL support for allocation/deallocation. The compound dispatcher gates these v4.2 operations and export write permission.

## Risks and Test Signals
Risks include offset+length overflow, stateid handling differences between special, lock, share, and delegation states, delegation conflict delays, backend fallocate support gaps, and quota accounting for deallocate. Test signals are valid allocate/deallocate with write opens, read-only open `OPENMODE`, anonymous stateid with delegation conflict, max-offset `FBIG`, zero-length no-op, quota denial, unsupported FSAL mapping, and state reference leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c -->
