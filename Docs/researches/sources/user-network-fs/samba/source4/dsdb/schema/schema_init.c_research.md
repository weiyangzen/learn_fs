# sources/user-network-fs/samba/source4/dsdb/schema/schema_init.c

## Purpose
`schema_init.c` creates, copies, loads, parses, and persists DSDB schema state from LDB and DRS prefix-map inputs.

## Important APIs, Types, and Functions
Schema allocation/copy APIs are `dsdb_new_schema` and `dsdb_schema_copy_shallow`. Prefix-map/schemaInfo APIs include `dsdb_load_prefixmap_from_drsuapi`, `dsdb_load_oid_mappings_ldb`, `dsdb_get_oid_mappings_drsuapi`, `dsdb_get_drsuapi_prefixmap_as_blob`, `dsdb_get_oid_mappings_ldb`, `dsdb_create_prefix_mapping`, `dsdb_write_prefixes_from_schema_to_ldb`, and `dsdb_read_prefixes_from_ldb`. Schema object parsers include `dsdb_attribute_from_ldb`, `dsdb_set_attribute_from_ldb_dups`, `dsdb_set_attribute_from_ldb`, `dsdb_set_class_from_ldb_dups`, `dsdb_set_class_from_ldb`, `dsdb_load_ldb_results_into_schema`, and `dsdb_schema_from_ldb_results`.

## Control Flow and Behavior
Schema creation starts with a zeroed schema. Shallow copy duplicates the prefix map and schemaInfo, memdups class/attribute records, and rebuilds sorted accessors. LDB prefix maps are parsed from `prefixMapBlob`, validated for DSDB version, converted through DRSUAPI prefix-map routines, and paired with validated `schemaInfo`. Prefix-map writes serialize the in-memory map back into the schema NC `prefixMap` attribute via `dsdb_replace` as system.

Attribute and class parsers use macros to read required and optional string, list, bool, uint32, GUID, and blob fields. Attribute parsing maps `attributeID` and `attributeSyntax` OIDs to ATTIDs, resolves syntax, creates an LDB schema attribute, and marks unique/single-valued/indexed flags. Class parsing maps `governsID`, reads superclass/containment/security fields, and adds the class. Duplicate-aware setters queue old schema objects for removal when a new object shares an ID.

`dsdb_schema_from_ldb_results` loads prefixMap and schemaInfo from the schema head, falls back to a default schemaInfo blob if absent, loads all attribute/class messages except the schema head, reads schema FSMO owner, and records whether the local NTDS Settings DN owns the schema FSMO.

## State and Persistence Behavior
The file mutates the in-memory `dsdb_schema` cache, including prefix map, schemaInfo, attributes, classes, sorted-accessor prerequisites, duplicate-removal queues, FSMO state, and schema update policy. It also persists prefix-map updates to the schema partition. `dsdb_create_prefix_mapping` temporarily swaps `schema->prefixmap` to write a new map, then restores the original so later schema reload observes disk state.

## Dependencies and Integration Points
It depends on NDR prefix-map/schemaInfo formats, ASN.1 BER OID helpers, DSDB prefix-map conversion, schema syntax lookup, LDB schema syntax registration, dlink lists, loadparm, `dsdb_replace`, schema accessor setup, and SAMDB DN helpers. It is used by schema FSMO loading, provisioning, replication schema update paths, and schema set/global schema code.

## Risks and Edge Cases
Required fields return `WERR_INVALID_PARAMETER` when absent; DRS replication can supply `name` instead of `cn`, which is specially handled. Prefix-map creation modifies persistent schema state inside a transaction-sensitive path and relies on a later reload to refresh the original schema object. The `GET_BLOB_LDB` macro steals blob data into the parsed object, so message lifetimes and talloc ownership matter. Confidential indexed attributes are deliberately not marked indexed to avoid timing leaks. Missing `schemaInfo` is tolerated with a generated default, but missing `prefixMap` is fatal. Shallow schema copies share many referenced strings and blobs.

## Test Signals
Tests should cover schema load from provision LDIF and live LDB, prefixMap/schemaInfo parse and write round trips, DRS prefix-map load, new prefix creation, required-field failures, `name` fallback for replicated objects, syntax resolution failures, confidential indexed attributes, duplicate replacement queues, FSMO owner detection, update-allowed loadparm, and shallow-copy accessor rebuilds.
