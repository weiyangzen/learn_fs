# sources/user-network-fs/samba/source4/dsdb/common/util_links.h

## Purpose
This header exposes the shared data structures used by DSDB linked-attribute search helpers. It lets callers prepare parsed-DN arrays and comparator context while hiding most implementation details in `util_links.c`.

## Important APIs, Types, and Functions
`struct compare_ctx` carries the target GUID, LDB context, talloc context, LDAP syntax OID, error code, invocation ID, extra-part blob, partial extra-part length, and comparison mode for linked-attribute searches. `struct parsed_dn` stores a lazily parsed `struct dsdb_dn`, the extracted GUID, and the original LDB value pointer. The only declared function is `get_parsed_dns_trusted(TALLOC_CTX *mem_ctx, struct ldb_message_element *el, struct parsed_dn **pdn)`, which builds the array shell from an LDB message element.

## Control Flow, State, and Persistence
There is no runtime logic in the header. The structures are caller-owned talloc state used during a single linked-attribute operation. `parsed_dn` intentionally permits deferred parsing by leaving `dsdb_dn` NULL until `util_links.c` needs the GUID or DN.

## Dependencies and Integration
The header assumes surrounding Samba includes provide `struct GUID`, `struct ldb_context`, `TALLOC_CTX`, `DATA_BLOB`, `bool`, `struct dsdb_dn`, `struct ldb_val`, and `struct ldb_message_element`. It is paired with `util_links.c` and integrated into DSDB link metadata/replication modules that need a common representation of link values.

## Risks
Because only `get_parsed_dns_trusted()` is declared here, any caller using `struct compare_ctx` directly is tightly coupled to `util_links.c` internals. The header relies on include order for type definitions. Mismanaging the lifetime of `struct ldb_message_element` values referenced by `parsed_dn.v` can leave dangling pointers.

## Test Signals
Build tests should cover include order through real DSDB modules. Runtime link tests should verify that arrays from `get_parsed_dns_trusted()` remain valid while the source LDB message is alive, are safely empty for zero values, and interact correctly with `parsed_dn_find()` in the implementation.
