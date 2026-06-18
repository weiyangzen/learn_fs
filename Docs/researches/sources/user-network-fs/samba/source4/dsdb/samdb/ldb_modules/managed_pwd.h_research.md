# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/managed_pwd.h

## Purpose
`managed_pwd.h` declares the constructed-attribute hook for `msDS-ManagedPassword`. It provides the include guard and forward declaration needed by other DSDB LDB module code to call into `managed_pwd.c` without exposing GMSA implementation details.

## Important APIs, types, and functions
The header includes `<ldb.h>`, forward-declares `struct ldb_module`, and declares:

`int constructed_msds_managed_password(struct ldb_module *module, struct ldb_message *msg, enum ldb_scope scope, struct ldb_request *parent, struct ldb_reply *ares);`

The signature matches Samba's constructed-attribute callback shape: module context, result message to augment, search scope, parent request for controls/security context, and reply object for reply controls.

## Control flow
There is no executable control flow in the header. It establishes the ABI contract used by the constructed-attribute registration site and implemented in `managed_pwd.c`.

## State and persistence behavior
The header defines no state. Its declared function constructs transient result data and may signal later GMSA persistence through reply controls, as described in the C implementation.

## Dependencies and integration points
The header is intentionally minimal: it depends only on LDB types and is consumed by DSDB module code that wires constructed attributes. Keeping GMSA internals out of the header limits rebuild coupling and keeps policy in `managed_pwd.c`.

## Risks and edge cases
Any signature drift between the constructed-attribute dispatcher and this declaration would be a compile-time or runtime integration break. Because `enum ldb_scope` is accepted but not used in the implementation, future callers should not assume scope-specific behavior without changing both files.

## Test signals
Compile coverage is the primary signal. Functional tests should request `msDS-ManagedPassword` through the constructed-attribute path rather than calling the implementation helper directly, proving the declared ABI is correctly wired.
