# sources/user-network-fs/samba/source4/dsdb/schema/schema_info_attr.c

## Purpose
`schema_info_attr.c` implements creation, validation, parsing, serialization, and comparison for the AD `schemaInfo` value carried in schema NC metadata and DRS prefix maps.

## Important APIs, Types, and Functions
Public functions are `dsdb_schema_info_new`, `dsdb_schema_info_blob_new`, `dsdb_schema_info_blob_is_valid`, `dsdb_schema_info_from_blob`, `dsdb_blob_from_schema_info`, and `dsdb_schema_info_cmp`. The wire/storage format is `struct schemaInfoBlob`, whose marker is expected to be `0xFF`.

## Control Flow and Behavior
New schemaInfo objects default to revision zero and GUID zero. New blobs allocate 21 zeroed bytes and set byte zero to `0xFF`. Parsing validates length and marker, NDR-decodes the blob, and copies revision/invocation ID. Serialization builds a `schemaInfoBlob` and NDR-encodes it. Comparison validates the last DRS prefix-map mapping as schemaInfo and accepts local schema revisions newer than the remote, reports schema mismatch for older local revision, reports schema conflict for equal revision but different invocation ID, and otherwise succeeds.

## State and Persistence Behavior
The schemaInfo blob is durable schema metadata stored in the schema NC and included as the final special entry in DRS OID mapping counters. The functions allocate parsed structures/blobs on caller contexts and do not change the schema except through caller assignment.

## Dependencies and Integration Points
It depends on DSDB utilities, SAMDB definitions, module utilities, NDR DRSUAPI/DRSBLOBS definitions, and GUID helpers. It integrates with `schema_init.c` and `schema_prefixmap.c` for prefix-map load/export and replication schema compatibility checks.

## Risks and Edge Cases
Only marker and length are checked before NDR parse. Comparison requires at least one mapping and a final `id_prefix == 0` schemaInfo entry. Equal revisions with different invocation IDs are conflicts; newer local revisions are accepted, which may mask backward compatibility gaps. A NULL `schema->schema_info` would crash callers of comparison.

## Test Signals
Tests should cover new object/blob defaults, invalid NULL/short/long/wrong-marker blobs, NDR parse/push round trips, DRS mapping with missing or malformed final schemaInfo, local newer/older/equal revisions, invocation ID conflicts, and zero revision initial replication behavior.
