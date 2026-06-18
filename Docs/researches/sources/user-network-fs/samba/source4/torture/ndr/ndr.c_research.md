# sources/user-network-fs/samba/source4/torture/ndr/ndr.c

## Purpose

`ndr.c` implements the shared local torture harness for NDR fixture tests and assembles the top-level local `ndr` suite. It provides helper functions used by protocol-specific files to register pull-only, pull/push-validate, in/out RPC, and invalid-data tests. It also contains direct unit tests for NDR utility behavior around string terminators, GUID parsing/formatting/blob packing, GUID comparison, and syntax ID parsing.

## Important APIs, types, and functions

`struct ndr_pull_test_data` stores a fixture `DATA_BLOB`, optional input-context blob for in/out RPC tests, structure size, generated pull/push/print function pointers, NDR direction flags, libndr flags, and expected NDR error. `_torture_suite_add_ndr_pullpush_test`, `_torture_suite_add_ndr_pull_inout_test`, and `_torture_suite_add_ndr_pull_invalid_data_test` are public helpers declared in `ndr.h` and called through macros by protocol suites.

Key wrappers are `wrap_ndr_pullpush_test`, `wrap_ndr_inout_pull_test`, and `wrap_ndr_pull_invalid_data_test`. Utility tests include `test_check_string_terminator`, `test_guid_from_string_null`, `test_guid_from_string_invalid`, `test_guid_from_string`, `test_guid_from_data_blob`, `test_guid_string_valid`, `test_guid_string2_valid`, `test_guid_into_blob`, `test_guid_into_long_blob`, `test_guid_into_short_blob`, `test_compare_uuid`, and `test_syntax_id_from_string`.

## Control flow

For a normal pull/push test, the wrapper creates an `ndr_pull` over the fixture, ORs in libndr flags, enables `LIBNDR_FLAG_REF_ALLOC`, decodes into zeroed talloc memory, computes the highest consumed offset from `offset` and `relative_highest_offset`, asserts that no bytes remain unread, invokes the optional typed checker, dumps decoded data and raw bytes through `torture_ndrdump`, then optionally pushes the decoded structure back and compares the output blob with the fixture.

For in/out RPC tests, the wrapper first decodes the `NDR_IN` context blob into the shared structure, then decodes the `NDR_OUT` blob over the same structure so response parsing has request context. Invalid-data tests invert the assertion: they pass only if the generated pull routine returns the expected `enum ndr_err_code`.

`torture_local_ndr` creates the top-level suite, adds many protocol sub-suites, then adds standalone utility tests.

## State and persistence

The harness has no persistent external state. Test state lives in `struct torture_test` data allocated below each tcase. `torture_ndr_push_struct_blob_flags` steals pushed blob data into the requested memory context, then frees the push context. Debug output behavior depends on `DEBUGLEVEL`, using direct debug printing at level 10 or string collection otherwise.

## Dependencies

The implementation depends on Samba torture core types, talloc, `librpc/ndr/libndr.h`, generated `ndr_misc` helpers for GUID tests, `dlinklist.h` for appending tests to tcases, and `param/param.h` through the local torture environment. It also depends on all protocol suite constructors declared in `torture/ndr/proto.h`.

## Integration points

This file is the central integration point for local NDR testing. The protocol suites researched in this subset, including LSA, NBT, Netlogon, NTLMSSP, and NEGOEX, are all added through `torture_local_ndr`. The helper APIs declared here and in `ndr.h` are the contract used by every small fixture suite.

## Risks

The full-consumption assertion is strong, but the push equality check only runs when a push function is provided by registration. Pull-only tests may miss encoder regressions. `test_guid_from_data_blob` defines two blobs but iterates from index 1, so the binary blob case appears skipped and only the hex-string blob is tested. `test_guid_from_string_valid` is a placeholder returning true. Some wrappers assume the typed checker casts are correct; the safety of that pattern depends on macro usage in `ndr.h`.

## Test signals

Strong signals include unread-byte detection, optional byte-identical re-encoding, `LIBNDR_FLAG_REF_ALLOC` pointer allocation behavior, explicit expected NDR errors for invalid data, GUID invalid-input coverage, fixed-size blob buffer-size errors, and syntax ID parse equality. The top-level suite membership is also a signal: if a protocol suite is not added here, its fixtures will not run under the local `ndr` target.
