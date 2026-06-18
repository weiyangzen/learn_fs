# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_remove.c

## Purpose
Implements NFSv4 REMOVE for unlinking a named child from the current directory and returning directory change info.

## Important APIs, Types, and Functions
- `nfs4_op_remove` handles `NFS4_OP_REMOVE`.
- Uses `nfs4_sanity_check_FH`, `nfs4_utf8string_scan`, `nfs_get_grace_status`, `fsal_remove`, `fsal_get_changeid4`, and FSAL attr preparation/release.
- `nfs4_op_remove_Free` is a no-op.

## Control Flow
The operation prepares parent pre/post change attribute lists, validates CurrentFH as a directory, validates the target as a path component, rejects during grace with `NFS4ERR_GRACE`, captures initial parent change, calls `fsal_remove`, and fills `cinfo.before`, `cinfo.after`, and `cinfo.atomic` from FSAL-returned attrs when available or live changeid fallback otherwise. It releases attr lists and the grace reservation on the path that acquired it.

## State and Persistence Behavior
Mutates filesystem namespace by removing a child. Also returns change info describing the parent directory before/after mutation. It does not mutate compound CurrentFH.

## Dependencies and Integration Points
Depends on FSAL namespace mutation, NFS grace-state gating, UTF-8 path-component validation, NFS status conversion, and tracing.

## Risks
Grace handling must call `nfs_put_grace_status` only after a successful `nfs_get_grace_status`. Change-info atomicity depends on whether the FSAL supplied both pre and post `ATTR_CHANGE`. UTF-8 validation must reject empty or path-like names.

## Test Signals
Test removing regular files and empty directories, non-directory CurrentFH, invalid names, removal during grace, FSAL errors such as NOENT/NOTEMPTY/ACCESS, and change-info atomic true/false cases.
