# sources/user-network-fs/samba/source4/dsdb/schema/schema.h

## Purpose
`schema.h` defines Samba's core in-memory AD schema model: syntax converters, attribute objects, class objects, schema cache state, schema query enums, conversion targets, and the generated schema API include.

## Important APIs, Types, and Functions
Key types are `enum dsdb_dn_format`, `struct dsdb_syntax_ctx`, `struct dsdb_syntax`, `struct dsdb_attribute`, `struct dsdb_class`, `enum schema_set_enum`, `struct dsdb_schema_info`, `struct dsdb_schema`, `enum dsdb_attr_list_query`, `enum dsdb_schema_convert_target`, and `dsdb_schema_refresh_fn`. Attribute/class macros `DSDB_SCHEMA_COMMON_ATTRS`, `DSDB_SCHEMA_ATTR_ATTRS`, and `DSDB_SCHEMA_CLASS_ATTRS` define common LDB load lists.

## Control Flow and Behavior
The header has no executable control flow, but it defines callback contracts for syntax validation and conversion between LDB values and DRSUAPI attributes. `struct dsdb_schema` stores sorted accessor arrays used by binary-search query helpers, FSMO ownership/update state, reload metadata, OID-conversion policy, and schema resolution flags.

## State and Persistence Behavior
`struct dsdb_schema` is a long-lived in-memory cache of persisted schema NC content: prefix map, schemaInfo, linked lists of attributes/classes, sorted indexes, removed-object queues for duplicate handling, FSMO owner state, last-change timestamps, metadata USN, and relaxed OID conversion policy. `struct dsdb_attribute` and `struct dsdb_class` mirror LDAP schema objects plus computed/internal fields such as syntax pointers, LDB schema attributes, possible inferiors, and subclass order.

## Dependencies and Integration Points
The header includes `prefixmap.h` and generated `dsdb/schema/proto.h`, and is included by SAMDB, schema loaders, syntax converters, objectclass modules, replication, and schema query code. Its fields are populated by `schema_init.c`, indexed by schema set code, queried by `schema_query.c`, and formatted by schema description/conversion code.

## Risks and Edge Cases
Because many modules inspect structure fields directly, layout or semantic changes are high risk. Shallow schema copies share many pointed-to strings/blobs and require stable source lifetimes. The distinction between class categories 0/1/2/3, systemOnly, isDefunct, and computed lists drives object validation and must match AD semantics. Relaxed OID conversion and resolving-in-progress flags can hide temporary schema lookup failures during replication.

## Test Signals
Signals include schema load from LDB/DRS, sorted accessor setup, syntax conversion validation, objectClass sorting, possibleInferiors construction, schemaInfo/prefixMap round trips, FSMO owner detection, and module compile coverage against generated prototypes.
