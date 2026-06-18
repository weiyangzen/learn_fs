# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/lazy_commit.c

## Purpose
`lazy_commit.c` advertises compatibility with the LDAP server lazy commit control by consuming it and forwarding an otherwise equivalent request. It does not implement deferred or relaxed durability; it simply marks `LDB_CONTROL_SERVER_LAZY_COMMIT` non-critical before passing the operation down.

## Important APIs, types, and functions
The single handler is `unlazy_op()`, wired into search, add, modify, delete, rename, generic request, and extended operation slots. It uses the appropriate `ldb_build_*_req()` helper for each operation and `dsdb_next_callback` for reply forwarding.

## Control flow
If the request lacks `LDB_CONTROL_SERVER_LAZY_COMMIT`, `unlazy_op()` returns `ldb_next_request(module, req)`. If present, it switches on `req->operation`, rebuilds a semantically equivalent child request with the same controls and payload, clears `control->critical`, and forwards the new request. Unsupported request types return `LDB_ERR_UNWILLING_TO_PERFORM`.

## State and persistence behavior
The module has no state and no direct persistence semantics beyond leaving the actual operation to lower modules. Its key behavior is to prevent a critical lazy-commit control from failing against backends that do not implement it.

## Dependencies and integration points
It depends only on LDB request builders and Samba's `dsdb_next_callback`. It should sit where controls can be consumed before a lower module rejects an unsupported critical control.

## Risks and edge cases
The name and control behavior can be misleading: callers may assume lazy commit semantics, but Samba performs normal commit behavior. Rebuilding every operation type must preserve controls, request ownership, and callback behavior; missing operation variants would cause compatibility failures.

## Test signals
Run each LDB operation type with and without `LDB_CONTROL_SERVER_LAZY_COMMIT`, including critical controls, and verify the lower operation succeeds normally, the control is marked non-critical, replies are propagated, and unsupported operations produce `LDB_ERR_UNWILLING_TO_PERFORM`.
