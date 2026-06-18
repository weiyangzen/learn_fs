# sources/user-network-fs/samba/source4/torture/ldap/schema.c

## Purpose

`schema.c` tests reading AD schema data over LDAP and constructing Samba's in-memory `dsdb_schema`. It then reports attribute categories such as not replicated, partial attribute set, constructed, syntax-sorted, and not-in-filtered-replica.

## Important APIs, Types, and Functions

- `struct test_rootDSE` stores default, root, configuration, and schema naming contexts.
- `struct test_schema_ctx` tracks paged-search control state and per-entry callback data.
- `test_search_rootDSE()` discovers naming contexts.
- `test_schema_search_callback()` handles paged LDB replies and updates cookies.
- `test_create_schema_type()` performs paged subtree searches under the schema DN.
- `test_add_attribute()` and `test_add_class()` feed LDAP messages into `dsdb_set_attribute_from_ldb()` and `dsdb_set_class_from_ldb()`.
- `test_create_schema()` builds a `struct dsdb_schema`.
- Dump helpers iterate schema attributes and print categories.
- `torture_ldap_schema()` orchestrates connection, schema construction, and dumps.

## Control Flow

After connecting to `ldap://<host>/`, the test reads RootDSE naming contexts, allocates an empty `dsdb_schema`, and fetches all `attributeSchema` and `classSchema` objects with the critical paged-results control. The callback increments counts, invokes the supplied schema-population callback for entries, and copies returned page cookies until no pending page remains. Dump helpers then iterate the populated linked lists and print attributes matching system flag, partial set, syntax OID, and filtered-replica criteria.

## State and Persistence Behavior

The test is read-only against LDAP. It creates transient in-memory schema state under the LDB context and emits diagnostic output.

## Dependencies and Integration Points

It depends on LDAP-backed LDB, paged-results controls, Samba DSDB schema conversion helpers, RootDSE naming context attributes, and `dsdb_attribute_is_attr_in_filtered_replica()`. It is registered as `ldap.schema`.

## Risks and Edge Cases

Paged-search control handling is sensitive to cookie ownership and request reuse. Schema conversion assumes all required schema attributes are present and compatible with Samba's DSDB parsers. Dump output is diagnostic rather than strictly asserted, so missing categories may not fail unless schema creation fails.

## Test Signals

Primary pass signals are successful RootDSE discovery, successful paged retrieval of attributeSchema/classSchema objects, successful conversion into `dsdb_schema`, and no failures in category iteration. Counts printed for each filter provide regression evidence.
