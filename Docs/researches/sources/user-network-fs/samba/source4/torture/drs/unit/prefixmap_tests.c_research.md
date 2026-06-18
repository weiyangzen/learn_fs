# sources/user-network-fs/samba/source4/torture/drs/unit/prefixmap_tests.c

## Purpose
This file defines the `drs.unit.prefixMap` torture test case for Samba's DSDB schema prefix map implementation. It validates OID prefix table construction, OID-to-ATTID conversion, ATTID-to-OID conversion, DRSUAPI mapping conversion, LDB blob conversion, and persistence of `prefixMap` data through a temporary LDB.

## Important APIs, Types, and Functions
The private fixture `struct drsut_prefixmap_data` owns two `dsdb_schema_prefixmap` fixtures (`pfm_new` and `pfm_full`), a default `dsdb_schema_info`, and a temporary `ldb_context`. `struct drsut_pfm_oid_data` describes expected prefix rows as an id, binary OID hex string, and human-readable OID prefix. `_prefixmap_test_new_data` encodes the default NewPrefixTable values from MS-DRSR, while `_prefixmap_full_map_data` models a fuller Windows Server 2008 clean-schema prefix map. `_prefixmap_test_data` drives OID/ATTID cases, including entries absent from the default map.

Core helpers are `_drsut_prefixmap_new()`, which constructs a `dsdb_schema_prefixmap` from static hex data using `strhex_to_data_blob()`, and `_torture_drs_pfm_compare_same()`, which compares prefix maps by length, id, and binary OID at each index. The tests exercise `dsdb_schema_pfm_new()`, `dsdb_schema_pfm_make_attid()`, `dsdb_schema_pfm_attid_from_oid()`, `dsdb_schema_pfm_oid_from_attid()`, `dsdb_drsuapi_pfm_from_schema_pfm()`, `dsdb_schema_pfm_contains_drsuapi_pfm()`, `dsdb_schema_pfm_from_drsuapi_pfm()`, `dsdb_get_oid_mappings_ldb()`, `dsdb_load_oid_mappings_ldb()`, `dsdb_write_prefixes_from_schema_to_ldb()`, `dsdb_read_prefixes_from_ldb()`, `dsdb_schema_pfm_copy_shallow()`, and `dsdb_create_prefix_mapping()`.

## Control Flow
`torture_drs_unit_prefixmap()` registers a fixture-backed torture tcase named `prefixMap`. Setup allocates the fixture, builds default and full prefix maps, obtains a default schemaInfo object from `drsut_schemainfo_new()`, and creates a temporary LDB containing a schema base DN with a placeholder `prefixMap` attribute. Individual tests then cover: default map construction; `make_attid` on full and initially small maps; lookup-only `attid_from_oid` without mutation; reverse `oid_from_attid`; rejected ATTID ranges; schema-prefixMap to DRSUAPI conversion and back; schema-prefixMap to LDB values and back; direct LDB read/write; and incremental prefix creation through `dsdb_create_prefix_mapping()`.

The `dsdb_create_prefix_mapping` test is the most stateful path. It writes the initial prefix map to LDB, then iterates over OID cases. For OIDs not present in the base map it predicts the new map by copying and extending the prefix map, calls `dsdb_create_prefix_mapping()`, asserts that the in-memory schema prefix map pointer and contents did not change immediately, and verifies that LDB now contains the predicted updated prefix map.

## State and Persistence Behavior
Most state is fixture-owned and freed by talloc teardown. Persistent behavior is limited to a temporary LDB created via `torture_temp_dir()`, `ldb_init()`, and `ldb_connect()`. Tests set the `"schemaNamingContext"` opaque to `CN=Schema,CN=Config`, add a schema base record, and write/read `prefixMap` plus `schemaInfo` through DSDB helpers. There is no durable repository or system state, but failed tests may leave temporary files under the torture temp area until harness cleanup.

## Dependencies and Integration Points
The file depends on Samba torture APIs, DSDB schema APIs, DRSUAPI structures, LDB, NDR data blob helpers, talloc, and `drsut_schemainfo_new()` from the schemaInfo unit tests. It integrates into the DRS torture module through `torture_drs_unit_prefixmap()` and is built by the neighboring DRS `wscript_build` as part of `TORTURE_DRS`.

## Risks
The tests assume exact prefix-map ordering, so legitimate implementation changes that preserve semantic lookup but reorder prefixes can fail. Several checks compare Windows-derived fixture data, which makes the file sensitive to schema fixture drift. LDB tests require the mock schema base DN and placeholder attribute to be shaped exactly as DSDB helper code expects. The small-map test intentionally allows new prefix ids to be implementation-dependent except for the ATTID low word; broadening that assertion would make the test brittle.

## Test Signals
Passing signals include exact default prefix map match, expected ATTID values for full maps, no mutation from lookup-only APIs, correct error codes for invalid ATTID ranges, successful DRSUAPI and LDB round trips including schemaInfo placement, and LDB updates that match predicted prefix map growth. Failures isolate prefix map creation, conversion, persistence, and mutation semantics.
