<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/dsdb_notification.c -->
# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/dsdb_notification.c

Purpose: `dsdb_notification.c` implements a simplified LDAP notification control for DSDB searches. Rather than holding a fully asynchronous persistent search, it stores a USN cookie in the request control and expects the LDAP layer/client to retry periodically; each subsequent call returns objects whose `uSNChanged` is greater than the previously observed high-water mark.

Important APIs, types, and functions: `struct dsdb_notification_cookie` holds `known_usn`. `dsdb_notification_verify_tree()` constrains accepted filters to Windows-compatible broad filters, allowing present tests on common attributes such as `objectClass`, `objectGUID`, `distinguishedName`, and `name`. `dsdb_notification_filter_search()` manages cookie setup and builds the USN search. `dsdb_notification_search()` detects `LDB_CONTROL_NOTIFICATION_OID`. `dsdb_notification_init()` registers the control.

Control flow: special DN searches and searches without the notification control pass through. Notification searches must have a parse tree accepted by `dsdb_notification_verify_tree()`. On the first call, the module allocates a cookie in `control->data`, marks the control non-critical/done, records the current highest sequence number, and returns success without entries. On later calls, it builds a replacement filter `uSNChanged > previous_known_usn`, updates `known_usn` to the current highest sequence number, and forwards a downstream search with the original base, scope, attrs, and controls.

State and persistence: no server-side persistent state exists. Progress is stored in the in-memory control data object across retries within the caller's control handling. The DB state consulted is only `LDB_SEQ_HIGHEST_SEQ` and `uSNChanged`.

Dependencies and integration points: the module depends on ldb parse trees, ldb sequence numbers, `LDB_CONTROL_NOTIFICATION_OID`, `dsdb_module_werror()` with `WERR_DS_NOTIFY_FILTER_TOO_COMPLEX`, and normal ldb search callback behavior through `dsdb_next_callback`.

Risks and edge cases: this is intentionally not a true async persistent search, so correctness depends on periodic retries by the LDAP server/client layer. The generated parse-tree uses `LDB_OP_GREATER` while comments describe `>=`, so boundary semantics depend on `known_usn + 1` formatting. Complex filters are rejected or, for OR, accepted if one branch is broad enough. `talloc_move(down_req, &filter_usn)` occurs before `down_req` is assigned, which is suspicious even if harmless in practice. If the caller loses control data, the next request restarts from the current high-water mark and misses older changes.

Test signals: direct test registration was not obvious in the searched selftest snippets, so this is probably covered through LDAP notification integration. Useful tests include first-call empty result with cookie creation, second-call results after modifications, rejected complex filters with `WERR_DS_NOTIFY_FILTER_TOO_COMPLEX`, OR/AND validation behavior, special-DN pass-through, and loss/reinitialization of cookie state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/dsdb_notification.c -->
