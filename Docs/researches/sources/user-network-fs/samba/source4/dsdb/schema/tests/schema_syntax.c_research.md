# sources/user-network-fs/samba/source4/dsdb/schema/tests/schema_syntax.c

## Purpose

`tests/schema_syntax.c` defines the local torture suite `dsdb.syntax`, which regression-tests selected DSDB syntax conversion callbacks by round-tripping known DRSUAPI wire blobs through LDB values and back. It focuses on representative Active Directory schema syntaxes that are easy to corrupt during replication compatibility changes.

## Important APIs, Types, And Functions

The local fixture type is `struct torture_dsdb_syntax`, holding a provisioned `ldb_context` and its `dsdb_schema`. `hexstr_to_data_blob()` converts hexadecimal test vectors to binary blobs. `torture_syntax_add_OR_Name()` injects an Exchange-like `authOrig` attribute with Object(OR-Name) syntax into the loaded schema so OR-Name conversion can be tested.

`torture_test_syntax()` is the shared assertion helper. It locates the syntax by standard OID, resolves the named schema attribute, asserts that the attribute uses the expected syntax, converts the DRS value to an LDB message element, compares the result to the expected LDB string, validates the LDB form, converts back to DRSUAPI, and compares the output blob to the original binary vector.

Individual test functions cover DN-BINARY, DN, OR-Name, INT32, INT64, NTTIME, BOOL, and UNICODE. `torture_dsdb_syntax_tcase_setup()` loads a provisioned schema via `provision_get_schema()`, obtains it with `dsdb_get_schema()`, and installs `authOrig`. `torture_dsdb_syntax()` registers the test case fixture and simple tests.

## Control Flow

The suite setup creates `priv`, loads the schema from disk-backed provision helpers, fetches the schema from the LDB opaque state, and mutates the schema by adding the OR-Name attribute. Each test passes a syntax OID, attribute display name, expected LDB string, and expected DRS hex string into the shared round-trip helper. Teardown unlinks the LDB from the fixture and frees the fixture context.

DN and DN-BINARY tests include extended GUID and SID components, so they exercise the NDR object identifier paths in `schema_syntax.c`. The OR-Name test reuses the DN-binary DRS encoding path but validates that the schema row maps to the OR-Name syntax and accepts the expected LDB DN form. The Unicode test includes accented text to verify UTF-16 to local charset conversion and back.

## State And Persistence Behavior

The tests allocate all state under torture/talloc contexts and do not persist database mutations beyond the fixture lifetime. The fixture does call `dsdb_set_schema(..., SCHEMA_WRITE)` after adding the synthetic `authOrig` attribute, so it exercises the same schema install path used by production code, including sorted accessor rebuilds and schema special record handling on the test LDB.

## Dependencies And Integration Points

The suite depends on Samba torture APIs, provision schema loading, LDB LDIF parsing, DSDB schema lookup/install APIs, DRSUAPI syntax callbacks, and binary assertion helpers. It is an integration-style test rather than a pure unit test because it relies on a real provisioned schema and actual syntax table lookups.

## Risks And Edge Cases

Coverage is intentionally narrow: the tests verify valid round trips but do not assert invalid syntax rejection, range checks, empty blob handling, remote prefix map translation, relaxed OID behavior, or outbound `msDS-IntId` selection. Test vectors are hard-coded, so changes in canonical DN linearization, charset behavior, or schema fixture content can break expected strings even when conversion semantics are otherwise acceptable. The synthetic OR-Name attribute must remain consistent with the syntax table's `oMSyntax`, `oMObjectClass`, and `attributeSyntax` matching logic.

## Test Signals

Passing this suite indicates that the selected syntax callbacks preserve byte-for-byte DRS representations through an LDB round trip for common AD cases. Failures point directly to syntax selection, DRS blob decoding/encoding, LDB validation, provision schema availability, or schema mutation via `dsdb_set_schema()`.
