# sources/user-network-fs/samba/source4/dsdb/schema/schema_set.c

## Purpose

`schema_set.c` installs, caches, refreshes, and persists Samba AD DS schema metadata on an `ldb_context`. It bridges the in-memory `struct dsdb_schema` representation with LDB runtime behavior by setting attribute handler overrides, building sorted lookup arrays, writing special LDB control records such as `@ATTRIBUTES` and `@INDEXLIST`, and attaching schema pointers or refresh hooks as LDB opaque values. It also supports provision-time schema loading from LDIF text and a process-wide shared schema used to reduce memory duplication.

## Important APIs, Types, And Functions

The main public entry points are `dsdb_set_schema()`, `dsdb_reference_schema()`, `dsdb_set_global_schema()`, `dsdb_get_schema()`, `dsdb_make_schema_global()`, `dsdb_set_schema_refresh_function()`, `dsdb_schema_set_indices_and_attributes()`, `dsdb_schema_fill_extended_dn()`, `dsdb_schema_set_el_from_ldb_msg[_dups]()`, and `dsdb_set_schema_from_ldif()`. They operate on `struct dsdb_schema`, `struct dsdb_attribute`, `struct dsdb_class`, `struct ldb_context`, `struct ldb_message`, and `enum schema_set_enum`.

`dsdb_attribute_handler_override()` maps LDB attribute names to schema-provided `ldb_schema_attribute` handlers via `dsdb_attribute_by_lDAPDisplayName()`. `dsdb_setup_sorted_accessors()` rebuilds all schema fast lookup arrays after applying queued class/attribute removals. It sorts classes by LDAP display name, governs ID numeric and OID forms, and CN; it sorts attributes by LDAP display name, attribute ID numeric and OID forms, `msDS-IntId`, link ID, and CN. `dsdb_setup_attribute_shortcuts()` derives DN-format shortcuts, `one_way_link`, and `bl_maybe_invisible` backlink visibility flags.

## Control Flow

`dsdb_set_schema()` is the normal local install path. It first calls `dsdb_setup_sorted_accessors()` so all lookup helpers are coherent, clears the `dsdb_use_global_schema` marker, stores `dsdb_schema` as an LDB opaque, steals the schema under the LDB talloc tree, writes or compares schema-backed LDB records according to the requested mode, and finally unlinks the prior schema reference.

`dsdb_schema_set_indices_and_attributes()` has two phases. It always installs the LDB schema override and optional GUID index override, then returns early for `SCHEMA_MEMORY_ONLY`. In write/compare modes it builds desired `@ATTRIBUTES` and `@INDEXLIST` messages, populates syntax approximations and indexed attributes, compares them against existing records with `ldb_msg_difference()`, and adds or modifies only when needed. `SCHEMA_COMPARE` avoids writes and reports `LDB_ERR_BUSY` if changes would be required outside an expected transaction.

`dsdb_get_schema()` chooses the current schema from either the global schema or the LDB opaque, optionally calls a registered refresh callback with recursion protection, and returns either the existing pointer or a talloc reference under the caller's context.

Provision-time loading in `dsdb_set_schema_from_ldif()` creates a new schema, marks its FSMO state as locally writable, loads prefix map and schemaInfo from one LDIF string, iterates class and attribute LDIF records from another string, installs the schema, and then rewrites default object category DNs with GUID extended components.

## State And Persistence Behavior

Persistent state is written into LDB special records. `@ATTRIBUTES` stores simplified per-attribute syntax hints such as `INTEGER`, `ORDERED_INTEGER`, and `CASE_INSENSITIVE` for bootstrap and schema-less operation. `@INDEXLIST` stores `@IDXONE`, optional GUID indexing keys, `@SAMDB_INDEXING_VERSION`, `SAMBA_FEATURES_SUPPORTED_FLAG`, and `@IDXATTR` entries for indexed non-confidential attributes. Confidential attributes are deliberately omitted from index declarations to avoid timing differences in search behavior.

Runtime state is held in LDB opaque values: `dsdb_schema`, `dsdb_use_global_schema`, `dsdb_schema_refresh_fn`, and `dsdb_schema_refresh_fn_private_data`. The file also owns the static `global_schema` pointer, reparented to the null talloc context by `dsdb_make_schema_global()`.

The `loadparm` option `dsdb:guid index` controls GUID index declaration. The `pack_format_override` opaque can suppress `ORDERED_INTEGER` declaration so older packing formats can be opened for downgrade scenarios without forcing old Samba versions to reject the database.

## Dependencies And Integration Points

This file is tightly integrated with LDB (`ldb_set_opaque`, `ldb_schema_attribute_set_override_handler`, `ldb_search`, `ldb_add`, `dsdb_modify`, `ldb_msg_difference`), talloc lifetime management, Samba schema helpers (`dsdb_attribute_by_*`, `dsdb_class_by_*`, `schema_fill_constructed`, LDIF schema loaders), loadparm configuration, NDR/GUID helpers, and linked-list utilities. It is used by provision, schema replication/loading, and DSDB modules needing current schema lookup or refresh.

## Risks And Edge Cases

Index persistence is security-sensitive: confidential attributes must remain excluded from `@IDXATTR`, and the `ORDERED_INTEGER` downgrade path intentionally writes less precise metadata. Incorrect changes can trigger reindexing, break older database compatibility, or expose timing differences. Global schema lifetime is process-wide and depends on careful talloc unlink/reference handling. `dsdb_get_schema()` logs fatal debug messages when refresh fails but falls back to the previous schema, so callers must not assume refresh success. `dsdb_schema_fill_extended_dn()` assumes default object category RDNs resolve to schema classes and fails hard on missing targets.

## Test Signals

Useful coverage comes from schema provision tests, DSDB module tests that load schemas, database upgrade/downgrade tests around indexing records, and replication tests that require `dsdb_get_schema()` refresh behavior. Direct assertions should check that sorted accessors are rebuilt after removals, confidential indexed attributes are omitted, GUID index toggles work, and `SCHEMA_COMPARE` refuses required writes.
