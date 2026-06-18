# sources/user-network-fs/samba/source4/dsdb/schema/schema_query.c

## Purpose
`schema_query.c` provides fast lookup and list-building helpers over a loaded DSDB schema, including attribute/class lookup by ID/OID/name, linked-attribute enumeration, full attribute-list computation, schemaIDGUID lookup, and objectClass ordering.

## Important APIs, Types, and Functions
Lookup APIs include `dsdb_attribute_by_attributeID_id`, `dsdb_attribute_by_attributeID_oid`, `dsdb_attribute_by_lDAPDisplayName`, `dsdb_attribute_by_lDAPDisplayName_ldb_val`, `dsdb_attribute_by_linkID`, `dsdb_attribute_by_cn_ldb_val`, `dsdb_class_by_governsID_id`, `dsdb_class_by_governsID_oid`, `dsdb_class_by_lDAPDisplayName`, `dsdb_class_by_lDAPDisplayName_ldb_val`, `dsdb_class_by_cn_ldb_val`, and `dsdb_lDAPDisplayName_by_id`. List helpers include `dsdb_linked_attribute_lDAPDisplayName_list`, `merge_attr_list`, `dsdb_attribute_list`, and `dsdb_full_attribute_list`. GUID helpers are `class_schemaid_guid_by_lDAPDisplayName` and `attribute_schemaid_guid_by_lDAPDisplayName`. `dsdb_sort_objectClass_attr` validates and sorts objectClass values.

## Control Flow and Behavior
Most lookups are binary searches over sorted arrays prepared elsewhere. `dsdb_attribute_by_attributeID_id` routes INTID-range IDs to the `attributes_by_msDS_IntId` index and ignores `0xFFFFFFFF` invalid placeholders. Attribute-list helpers merge may/must/system lists for one class, then recursively include auxiliary classes. Full lists are sorted case-insensitively and deduplicated.

`dsdb_sort_objectClass_attr` validates every supplied objectClass against the schema, rejects defunct classes, inserts `top` once, ensures missing superclass chain elements are present, then orders classes by `subClass_order` while placing structural/type-88 classes after auxiliary/abstract classes at the same hierarchy level. It writes a normalized output message element.

## State and Persistence Behavior
Lookup helpers are read-only against schema state. Attribute-list helpers allocate returned lists on caller contexts. ObjectClass sorting allocates new LDB values on the caller context and does not mutate the schema.

## Dependencies and Integration Points
The file depends on sorted schema accessor arrays, binary-search macros, string-list helpers, dlink lists, and subclass order computed by `schema_inferiors.c`/schema setup. It is used by schema validation, objectclass modules, schema description/export, replication conversion, and access-check code needing schemaIDGUIDs.

## Risks and Edge Cases
Sorted accessor arrays must be current; stale or unsorted arrays produce wrong lookup results. `strcasecmp_with_ldb_val` handles non-NUL-terminated LDB values but assumes string semantics. `dsdb_linked_attribute_lDAPDisplayName_list` sets a NULL terminator only if the allocated slot is not already NULL, which is fragile after `talloc_realloc`. Recursive auxiliary-class list building can loop if schema auxiliary relationships are cyclic. `dsdb_sort_objectClass_attr` relies on valid `subClass_order`; unknown parent chains or missing top can lead to NULL objectclass entries if earlier schema construction failed.

## Test Signals
Tests should cover every lookup index, INTID versus prefix-map ATTID routing, invalid ID handling, non-NUL LDB value lookup, linked-attribute list termination, may/must/system/full attribute lists with auxiliary classes and duplicates, schemaIDGUID lookup misses, objectClass sorting with missing parents, defunct/unknown classes, duplicate top, structural ordering, and cyclic auxiliary-class definitions.
