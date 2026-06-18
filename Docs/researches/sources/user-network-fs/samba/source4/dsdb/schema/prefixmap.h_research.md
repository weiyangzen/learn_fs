# sources/user-network-fs/samba/source4/dsdb/schema/prefixmap.h

## Purpose
`prefixmap.h` declares the in-memory data structures for DSDB prefix maps, which translate between Active Directory ATTID values and OID prefixes.

## Important APIs, Types, and Functions
It defines `enum dsdb_attid_type` for PFM, INTID, reserved, and internal ATTID ranges; `struct dsdb_schema_prefixmap_oid` for one prefix-map entry with an id and partial binary OID; and `struct dsdb_schema_prefixmap` for the prefix array and length.

## Control Flow and Behavior
No code is implemented here. The range categories guide `schema_prefixmap.c` and `schema_query.c` decisions such as whether an ATTID resolves through the prefix map or the `msDS-IntId` index.

## State and Persistence Behavior
The structures are the in-memory representation of prefix maps persisted in the schema NC `prefixMap` attribute and transferred over DRSUAPI. Binary OID blobs are talloc-owned by the containing prefix map.

## Dependencies and Integration Points
The header depends on `DATA_BLOB` being available through including contexts and is included by `schema.h`. It is consumed by schema initialization, prefix-map conversion, syntax conversion, and query lookup code.

## Risks and Edge Cases
The enum ranges encode protocol semantics from MS-ADTS and must remain aligned with `dsdb_pfm_get_attid_type`. Shallow copies of prefix map entries share blob pointers, so callers must respect talloc ownership and lifetime.

## Test Signals
Compile coverage plus prefix-map round trips should verify ATTID range classification, copied prefix lifetimes, and DRS/LDB serialization compatibility.
