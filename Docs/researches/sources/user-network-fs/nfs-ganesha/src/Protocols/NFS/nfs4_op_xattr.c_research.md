# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_xattr.c

## Purpose
Implements NFSv4 extended attribute operations: GETXATTR, SETXATTR, LISTXATTR, and REMOVEXATTR. It gates on FSAL xattr support, handles xattr value/list memory, performs response-size checks, and returns change info for mutating operations.

## Important APIs, Types, and Functions
- `nfs4_op_getxattr`, `nfs4_op_setxattr`, `nfs4_op_listxattr`, and `nfs4_op_removexattr` are the handlers.
- Uses FSAL object ops `getxattrs`, `setxattrs`, `listxattrs`, and `removexattrs`.
- Checks `ATTR4_XATTR` through `fs_supported_attrs`.
- Uses `nfs_get_grace_status`, `fsal_get_changeid4`, `check_resp_room`, and status conversion helpers.
- Free hooks release GETXATTR value strings and LISTXATTR name arrays.

## Control Flow
GETXATTR validates CurrentFH, checks xattr support, tries a 1024-byte value buffer, handles `ERR_FSAL_XATTR2BIG` by querying required size with a null buffer and retrying, checks response room, and transfers the value to the response. SETXATTR validates support and grace state, fills non-atomic before change info, calls `setxattrs`, sets after change on success, and releases grace. LISTXATTR validates support, enforces minimum `lxa_maxcount`, subtracts XDR overhead to compute the FSAL name budget, calls `listxattrs`, computes exact response size, and transfers the FSAL-allocated list. REMOVEXATTR mirrors SETXATTR using `removexattrs`.

## State and Persistence Behavior
SETXATTR and REMOVEXATTR mutate filesystem xattrs and return change info with `atomic = false`. GETXATTR and LISTXATTR allocate response memory. No NFS client/session state is changed.

## Dependencies and Integration Points
Depends on FSAL xattr capability and object xattr ops, NFSv4 xattr XDR types, grace-state gating for mutation, response room checks, and FSAL changeid retrieval.

## Risks
LISTXATTR performs the same sanity check twice, likely harmless but noisy. Mutating xattr ops call `nfs_put_grace_status` only after successful grace acquisition, but early error paths must stay balanced. GETXATTR's two-step size query depends on FSAL convention for `ERR_FSAL_XATTR2BIG`. Response-size overflow or allocation failure handling is sparse.

## Test Signals
Test unsupported xattrs, GETXATTR small/large/missing values, LISTXATTR too-small maxcount, paginated LISTXATTR cookies and EOF, response-room overflow cleanup, SETXATTR create/replace modes, REMOVEXATTR missing names, grace rejection, change-info before/after behavior, and free hooks under partial allocation.
