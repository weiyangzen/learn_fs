# sources/user-network-fs/samba/source4/torture/drs/drs_util.c Research

## Purpose
This file provides shared C utility functions for DRSUAPI torture tests. It decodes DRS attribute IDs into OID strings using a prefix map and loads a DSDB schema into an LDB connection from DRSUAPI prefix-map data.

## Important APIs, Types, And Functions
`drs_util_oid_from_attid()` implements the MS-DRSR attribute ID decoding algorithm. It splits an `attid` into high and low words, verifies the final prefix-map entry is the special schema-info entry, finds the matching prefix mapping, appends a BER encoded low word, and converts the binary OID with `ber_read_OID_String()`. `drs_util_dsdb_schema_load_ldb()` checks for an existing schema, builds a new schema, loads the DRS prefix map, searches for `attributeSchema` and `classSchema` objects, imports them into DSDB schema state, and attaches the schema with `dsdb_set_schema()`.

## Control Flow
Both functions are assertion-heavy test helpers. Malformed prefix maps, allocation failures, missing schema base DN, failed searches, schema conversion failures, or schema attachment failures trigger torture assertions or failures. Successful paths return `true`.

## State And Persistence
`drs_util_oid_from_attid()` allocates temporary binary OID data and returns the decoded OID under the torture context. `drs_util_dsdb_schema_load_ldb()` mutates the in-memory state of the supplied LDB by installing a schema; it does not write schema objects.

## Dependencies And Integration Points
The file depends on generated DRSUAPI types, DSDB schema helpers, SamDB, LDB, ASN.1 BER OID decoding, and the smbtorture assertion framework. It supports tests that consume `DsGetNCChanges()` schema or prefix-map responses.

## Risks And Test Signals
Signals are successful OID decoding and LDB schema attachment. Risks include trusting `prefix_map->num_mappings - 1` without a zero-count guard, strict assumptions about the special final mapping, and fatal assertions rather than recoverable errors.
