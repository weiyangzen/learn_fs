<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c

## Purpose
Implements NFSv4 `OP_ACCESS`, reporting which requested access bits are supported and currently permitted for the compound current file handle.

## APIs, Types, and Functions
Exports `nfs4_op_access()` and `nfs4_op_access_Free()`. It uses `ACCESS4args`, `ACCESS4res`, `compound_data_t`, `nfs4_sanity_check_FH()`, `nfs_access_op()`, `nfs4_Errno_status()`, and LTTng tracepoints. For minor version 4.2 and newer it permits xattr access bits `ACCESS4_XAREAD`, `ACCESS4_XAWRITE`, and `ACCESS4_XALIST`.

## Control Flow, State, and Persistence
The handler initializes supported/access output to zero, validates the current file handle with no specific file type, rejects unknown access bits above the allowed mask, and calls `nfs_access_op()` to perform the FSAL access check. FSAL success and access denial both return `NFS4_OK` because denial is represented by clearing bits; other FSAL errors map to protocol status. It does not alter filesystem or compound state.

## Dependencies and Integration
Depends on `compound_data_t->current_obj` being set by a prior PUTFH/lookup operation and on shared access conversion code. The compound dispatcher applies export metadata-read permission before this handler runs.

## Risks and Test Signals
Risks include bad max-access masks by minor version, confusion between protocol success and denied bits, and FSAL access implementations returning hard errors for ordinary denials. Test signals are access probes across file types, denied permissions returning `NFS4_OK` with cleared bits, xattr bits only for v4.2+, empty current FH errors, and tracepoint/status parity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c -->
