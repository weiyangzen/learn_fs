# sources/user-network-fs/samba/source4/torture/drs/unit/schemainfo_tests.c

## Purpose
This file defines `drs.unit.schemaInfo`, a DSDB/DRSUAPI schemaInfo torture unit suite. It validates construction, binary blob conversion, schemaInfo comparison semantics, and LDB module read/write/update helpers for the schemaInfo attribute used by Active Directory schema replication.

## Important APIs, Types, and Functions
`SCHEMA_INFO_INIT_STR` and `SCHEMA_INFO_DEFAULT_STR` define canonical 21-byte schemaInfo blobs: marker `0xFF`, revision, and invocation GUID. `struct schemainfo_data` stores a parsed blob, expected `dsdb_schema_info`, expected `WERROR`, and whether reverse conversion should be tested. `struct drsut_schemainfo_data` owns the temporary LDB, mock `ldb_module`, mock `dsdb_schema`, initial `schema_info`, and expanded test vector array. The `torture_assert_schema_info_equal` macro checks revision and invocation id.

Key helpers are `_drsut_schemainfo_new()`, public `drsut_schemainfo_new()`, `_drsut_ldb_schema_info_reset()`, and `_drsut_ldb_setup()`. Tests call `dsdb_schema_info_new()`, `dsdb_schema_info_blob_new()`, `dsdb_schema_info_from_blob()`, `dsdb_blob_from_schema_info()`, `dsdb_schema_info_cmp()`, `dsdb_module_schema_info_blob_write()`, `dsdb_module_schema_info_blob_read()`, and `dsdb_module_schema_info_update()`.

## Control Flow
Setup expands the static schemaInfo vectors into parsed `DATA_BLOB` and `GUID` structures, creates a wrapped temporary LDB, sets `"schemaNamingContext"`, adds an initial `schemaInfo`, creates a mock LDB module, creates a mock schema, pre-caches `"cache.invocation_id"`, and starts an LDB transaction. The test cases then validate default constructor output, parsing valid and invalid blobs, reverse blob generation for valid vectors, comparison behavior against malformed and revision-conflict DRSUAPI mapping containers, module-level blob write/read, and module-level schemaInfo update.

`test_dsdb_schema_info_cmp()` is the main behavioral matrix. It checks missing mapping data, empty schemaInfo mapping, invalid length, invalid marker, older remote schema acceptance, invalid id prefix rejection, equal schema acceptance, newer revision mismatch, newer revision with different invocation id mismatch, older revision with different invocation id acceptance, and same revision with different invocation id conflict.

## State and Persistence Behavior
The suite writes schemaInfo values into a temporary LDB record at the schema base DN and runs all tests inside one transaction. Teardown commits the transaction so failures can still expose LDB state during diagnostics, then frees the fixture. The tests manipulate mock LDB state but do not persist production SAM database data.

## Dependencies and Integration Points
The file depends on Samba torture, DSDB/SAMDB, DSDB LDB module utilities, `ldb_wrap`, DRSUAPI/NDR structures, loadparm, talloc, and GUID parsing. `drsut_schemainfo_new()` is intentionally public within the DRS torture unit area and is used by the prefixMap tests for schemaInfo fixture creation. The suite is registered through `torture_drs_unit_schemainfo()` and built into `TORTURE_DRS`.

## Risks
The tests encode exact binary schemaInfo layout and comparison policy, so changes to marker, length, revision semantics, or invocation-id conflict handling need corresponding fixture updates. The transaction commit in teardown means a setup failure after LDB allocation can still attempt commit; the code comments acknowledge teardown runs after partial setup. Mocking the LDB module is lightweight and may not catch behavior that depends on a full module stack.

## Test Signals
Passing signals include valid 21-byte schemaInfo round trips, invalid blob rejection, correct default zero schemaInfo construction, expected schema mismatch/conflict codes, successful module blob persistence, and update behavior that writes the schema's default invocation id/revision into LDB.
