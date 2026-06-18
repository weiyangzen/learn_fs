# sources/user-network-fs/samba/source4/dsdb/common/util.h

## Purpose
This header defines shared DSDB utility constants and a small public surface used by source4 DSDB/SAMDB code. Its main role is to provide the flag bitmask consumed by `dsdb_request_add_controls()` and wrappers such as `dsdb_search()`, `dsdb_add()`, `dsdb_modify()`, and `dsdb_delete()`, plus common secret/password attribute lists and LDB opaque names for session information.

## Important APIs, Types, and Functions
The `DSDB_SEARCH_*`, `DSDB_MODIFY_*`, and `DSDB_FLAG_*` constants map high-level DSDB operation needs to LDB controls. Examples include all-partition search, show deleted/recycled objects, extended DN display, reveal internals, relax/permissive modify, as-system execution, tree delete, provisioning, bypass-password-hash, no-global-catalog, partial replica modify, bypass last-set, replicated link handling, untrusted request marking, and managed-password refresh. `DSDB_SECRET_ATTRIBUTES_EX`, `DSDB_SECRET_ATTRIBUTES`, `DSDB_PASSWORD_ATTRIBUTES`, and `DSDB_AUTHENTICATION_ATTRIBUTES` define sensitive or authentication-relevant attribute lists used by modules and filtering logic. The header declares `dsdb_werror_at()` and convenience macros `dsdb_werror()` and `dsdb_module_werror()`. It also defines `struct dsdb_ldb_dn_list_node`, a linked-list node carrying a partition DN.

## Control Flow, State, and Persistence
There is no runtime control flow in the header. Its flags become runtime behavior only when passed into `dsdb_request_add_controls()` in `util.c`. `DSDB_SESSION_INFO` and `DSDB_NETWORK_SESSION_INFO` name LDB opaque values that other DSDB modules use to pass session/authentication context through the LDB layer. The secret/password/authentication attribute macros do not persist state themselves, but they centralize which attributes are treated as secret or password-adjacent in replication, logging, and filtering code.

## Dependencies and Integration
The header includes `libcli/util/werror.h`, forward-declares `struct GUID` and `struct ldb_context`, and assumes broader Samba include order for LDB and talloc-related types used elsewhere. It is included by `util.c`, SAMR utilities, group expansion, and DSDB modules that need common flags or error-reporting wrappers. The comments note that module-specific high bits for these flags live in `dsdb/samdb/ldb_modules/util.h`, so callers must treat the bit space as shared.

## Risks
The primary risk is flag drift: adding a flag here without implementing it in `dsdb_request_add_controls()` or colliding with module-function high bits can make callers believe a control was applied when it was not. The secret-attribute list is security-sensitive; omissions can leak password or trust material to RODCs/logs/replication paths, while over-inclusion can unnecessarily suppress legitimate attributes. Because many callers combine flags with bitwise OR, test coverage should catch invalid or contradictory combinations.

## Test Signals
Build coverage should catch missing declarations. Runtime tests should verify each public `DSDB_*` flag results in the expected LDB control, secret/password attribute lists match RODC and password logging expectations, `dsdb_werror()` formats WERROR codes into LDB errstrings with call-site data, and `DSDB_MARK_REQ_UNTRUSTED` affects request trust state without requiring an LDB control object.
