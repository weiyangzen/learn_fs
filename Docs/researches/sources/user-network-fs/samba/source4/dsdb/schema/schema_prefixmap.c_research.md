# sources/user-network-fs/samba/source4/dsdb/schema/schema_prefixmap.c

## Purpose
`schema_prefixmap.c` implements the DSDB prefix-map algorithms that translate between object/attribute OIDs and DRS ATTID values, and convert prefix maps between internal and DRSUAPI forms.

## Important APIs, Types, and Functions
Public APIs include `dsdb_pfm_get_attid_type`, `dsdb_schema_pfm_new`, `dsdb_schema_pfm_copy_shallow`, `dsdb_schema_pfm_add_entry`, `dsdb_schema_pfm_find_binary_oid`, `dsdb_schema_pfm_find_oid`, `dsdb_schema_pfm_make_attid`, `dsdb_schema_pfm_attid_from_oid`, `dsdb_schema_pfm_oid_from_attid`, `dsdb_schema_pfm_from_drsuapi_pfm`, `dsdb_drsuapi_pfm_from_schema_pfm`, and `dsdb_schema_pfm_contains_drsuapi_pfm`. Internal helpers include `_dsdb_schema_prefixmap_talloc`, `_dsdb_pfm_make_binary_oid`, `dsdb_schema_pfm_make_attid_impl`, and `_dsdb_drsuapi_pfm_verify`.

## Control Flow and Behavior
The initial prefix map is created from the standard AD prefix list defined by MS-DRSR. Full OIDs are BER-encoded, then truncated to a partial binary OID by removing the final subidentifier; that partial prefix is looked up in the map. ATTIDs are composed from the prefix-map entry ID in the high word and a low-word encoding of the final OID subidentifier, with a high bit marker when the subidentifier exceeds 14 bits. Read-only lookup fails if the OID prefix is absent, while make mode adds a new prefix entry and assigns either a nonconflicting remote ID or the next local ID.

OID-from-ATTID reverses that process for prefix-map ATTID ranges, reconstructing the BER OID and decoding it. DRSUAPI conversion verifies mapping arrays, optionally validates/parses a final schemaInfo entry, copies binary OID blobs into internal prefix-map entries, and can append schemaInfo when exporting. Containment comparison checks that a local prefix map contains every remote prefix, excluding the schemaInfo entry.

## State and Persistence Behavior
Prefix maps are in-memory arrays of talloc-owned binary OID prefixes, but they correspond to persisted schema NC `prefixMap` values and DRS replication mapping counters. `dsdb_schema_pfm_add_entry` mutates the map in place by reallocating the prefix array and duplicating the new blob under the map.

## Dependencies and Integration Points
The file depends on ASN.1 BER OID helpers, DRSUAPI/DRSBLOBS generated types, schemaInfo helpers, talloc data blobs, and Samba numeric parsing. It is called by schema initialization, schema syntax conversion, replication, and schema query ATTID resolution.

## Risks and Edge Cases
Only one- or two-byte final subidentifier encodings are handled when trimming and reconstructing OIDs; extremely large final subidentifiers could be invalid or mishandled. `dsdb_schema_pfm_oid_from_attid` rejects INTID/reserved/internal ranges, which must be resolved elsewhere. Shallow copies duplicate entry structs but not blob storage. DRS verification rejects empty OIDs and schemaInfo-like normal entries, but does not enforce unique IDs or prefixes. ATTID low-word truncation for large subidentifiers follows protocol behavior but can be surprising.

## Test Signals
Tests should cover ATTID range classification, standard prefix initialization, OID-to-ATTID and ATTID-to-OID round trips, absent prefix read-only failure, prefix addition and ID allocation, remote ID collision handling, DRS import/export with and without schemaInfo, malformed DRS maps, containment mismatch, and large final OID subidentifier behavior.
