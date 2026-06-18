# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readlink.c

## Purpose
Implements NFSv4 READLINK for symbolic links. It validates the current file handle, asks the FSAL for the link target, checks response room, and frees target storage through the operation free hook.

## Important APIs, Types, and Functions
- `nfs4_op_readlink` handles `NFS4_OP_READLINK`.
- `fsal_readlink` fills the result `utf8string`.
- `check_resp_room` accounts for status, XDR string length, and payload.
- `nfs4_op_readlink_Free` releases `READLINK4resok.link.utf8string_val` on success.

## Control Flow
The operation sets `resp->resop`, validates CurrentFH as `SYMBOLIC_LINK`, calls `fsal_readlink(data->current_obj, link_buffer)`, converts FSAL errors, computes the rounded response size, and either records `data->op_resp_size` or frees the link target if response size cannot fit.

## State and Persistence Behavior
No persistent state changes occur. The only owned state is the FSAL-allocated link buffer stored in the response and released by `nfs4_op_readlink_Free`.

## Dependencies and Integration Points
Depends on filehandle sanity checking, FSAL symlink target retrieval, NFS error conversion, response room tracking, and LTTng tracepoints. It participates in compound processing through CurrentFH and response-size accounting.

## Risks
The main risk is ownership of `utf8string_val`: it must be freed on response-size failure and after successful XDR use, but not after FSAL errors that did not allocate it. Long symlink targets must be rounded correctly for response-size checks.

## Test Signals
Test successful READLINK, non-symlink CurrentFH, stale/no filehandle errors, FSAL readlink failures, response-room overflow with long targets, and memory cleanup on both success and overflow.
