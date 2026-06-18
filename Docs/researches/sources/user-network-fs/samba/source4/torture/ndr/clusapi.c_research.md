# sources/user-network-fs/samba/source4/torture/ndr/clusapi.c

## Purpose
`clusapi.c` validates NDR parsing and round-trip encoding of Windows Cluster API property lists. It embeds two `clusapi_PROPERTY_LIST` byte streams and verifies that Samba decodes property counts, property names, syntaxes, sizes, value buffers, padding, and end markers exactly.

## Important APIs, types, and functions
- `clusapi_PROPERTY_LIST_data` is a six-property fixture with quorum and cluster storage settings: `FixQuorum`, `PreventQuorum`, `IgnorePersistentStateOnStartup`, `SharedVolumesRoot`, `WitnessDynamicWeight`, and `AdminAccessPoint`.
- `clusapi_PROPERTY_LIST_check` validates the first fixture, including DWORD blobs for zero/one values and an SZ value decoded as `C:\ClusterStorage`.
- `clusapi_PROPERTY_LIST_data2` is a twelve-property node/version fixture containing `NodeName`, version/build fields, `CSDVersion`, `NodeInstanceID`, drain fields, `DynamicWeight`, and `NeedsPreventQuorum`.
- `clusapi_PROPERTY_LIST_check2` validates the second fixture, including empty strings, GUID-like strings, DWORDs, and nonzero padding lengths.
- `ndr_clusapi_suite(TALLOC_CTX *ctx)` registers both fixtures as pull/push validation tests for `clusapi_PROPERTY_LIST`.

## Control flow
The suite creates a `clusapi` child suite and adds two `torture_suite_add_ndr_pull_validate_test` cases. For each fixture, the shared NDR harness pulls bytes into `struct clusapi_PROPERTY_LIST`, calls the relevant checker, pushes the structure back out, and validates byte stability. The checkers create expected four-byte `DATA_BLOB` values for DWORD zero, one, and selected version constants using `SIVAL`; they compare raw buffers with `torture_assert_data_blob_equal`. For string property values, they call `pull_reg_sz` to convert registry-style UTF-16LE `REG_SZ` buffers into C strings before comparing.

## State and persistence behavior
The file has no durable state. Static fixtures are immutable. Checkers allocate short temporary `DATA_BLOB` objects and release them with `data_blob_free`; decoded strings are talloc-owned by the torture context through `pull_reg_sz`.

## Dependencies and integration points
Dependencies include generated Cluster API NDR declarations from `librpc/gen_ndr/ndr_clusapi.h`, registry string conversion from `libcli/registry/util_reg.h`, Samba `DATA_BLOB` helpers, `SIVAL`, and NDR torture macros. The parent `ndr.c` test suite integrates this file through `ndr_clusapi_suite(suite)`.

## Risks and edge cases
- The tests assume fixed property ordering and exact byte layout. That is useful for NDR compatibility but does not cover unordered lookup behavior.
- The check functions are long and repetitive; copy/paste mistakes in expected sizes, property indexes, or assertion labels could reduce diagnostic quality.
- Coverage is limited to list-value DWORD and SZ syntaxes represented by the fixtures; other Cluster property syntaxes and malformed lists are not tested here.
- The validators rely on `pull_reg_sz` for string interpretation, so a failure could come from either Cluster API NDR parsing or registry string conversion.

## Test signals
Passing tests show that Samba can decode and byte-stably re-encode real-world Cluster API property lists with mixed DWORD and UTF-16LE string values, including DWORD buffers, padding fields, and `CLUSPROP_SYNTAX_ENDMARK` handling.
