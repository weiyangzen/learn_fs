<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c

## Purpose
Provides the NFSv4 `OP_DELEGPURGE` handler, currently implemented as unsupported.

## APIs, Types, and Functions
Exports `nfs4_op_delegpurge()` and `nfs4_op_delegpurge_Free()`. It touches `DELEGPURGE4args` only as an unused placeholder, fills `DELEGPURGE4res`, sets `resp->resop = NFS4_OP_DELEGPURGE`, and returns `NFS4ERR_NOTSUPP`.

## Control Flow, State, and Persistence
The handler does no validation of clientid or delegation state because the operation is not supported. It deterministically returns `NFS_REQ_ERROR` with protocol status `NFS4ERR_NOTSUPP`. No persistent state changes occur.

## Dependencies and Integration
The operation is still present in `optabv4[]`, so compounds containing it dispatch here and stop at this error. The free callback is a no-op because no dynamic response data is allocated.

## Risks and Test Signals
Risks are mostly protocol-coverage gaps: clients expecting delegation purge semantics will fail, and future implementation must revisit clientid validation and delegation cleanup. Test signals are compounds containing `DELEGPURGE` returning `NFS4ERR_NOTSUPP`, no result memory leaks, and dispatcher behavior stopping the compound after the error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c -->
