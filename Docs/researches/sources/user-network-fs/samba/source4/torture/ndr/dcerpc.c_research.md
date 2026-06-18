# sources/user-network-fs/samba/source4/torture/ndr/dcerpc.c

## Purpose
`dcerpc.c` adds regression coverage for DCE/RPC connection-oriented packet NDR parsing, specifically minimal `CO_CANCEL` and `ORPHANED` packet types. It verifies that Samba's `ncacn_packet` decoder selects the correct union arm and preserves header flags, data representation, fragment lengths, call IDs, and empty authentication trailers.

## Important APIs, types, and functions
- `ncacn_packet_co_cancel_data` is a 16-byte little-endian DCE/RPC packet with `ptype` `DCERPC_PKT_CO_CANCEL`, flags `LAST | PENDING_CANCEL_OR_HDR_SIGNING`, fragment length 16, auth length 0, and call ID 1.
- `ncacn_packet_co_cancel_check` validates the decoded `struct ncacn_packet` and its `u.co_cancel.auth_info`.
- `ncacn_packet_orphaned_data` is a 16-byte packet with `ptype` `DCERPC_PKT_ORPHANED`, flags `FIRST | LAST`, fragment length 16, auth length 0, and call ID 8.
- `ncacn_packet_orphaned_check` validates the decoded `u.orphaned.auth_info`.
- `ndr_dcerpc_suite(TALLOC_CTX *ctx)` creates a parent `dcerpc` suite and nested `co_cancel` and `orphaned` suites.

## Control flow
The suite factory creates nested suites for the two packet types, attaches them to the parent, and registers one `torture_suite_add_ndr_pull_validate_test` for each. The shared NDR harness decodes the byte array through generated `ndr_pull_ncacn_packet`, calls the packet-specific checker, then pushes the structure back out and compares to the original input. The checkers assert each fixed header field and ensure that the selected union arm has an empty `DATA_BLOB` authentication field.

## State and persistence behavior
There is no persistent state. The file contains two immutable 16-byte fixtures and allocates only transient suite/test objects under the supplied talloc context.

## Dependencies and integration points
The file depends on generated DCE/RPC NDR declarations from `librpc/gen_ndr/ndr_dcerpc.h`, DCE/RPC constants such as `DCERPC_PKT_CO_CANCEL`, `DCERPC_PKT_ORPHANED`, `DCERPC_PFC_FLAG_*`, and `DCERPC_DREP_LE`, plus the generic NDR torture helpers. The parent NDR runner includes it via `ndr_dcerpc_suite(suite)`.

## Risks and edge cases
- Only minimal packets with no auth data and no body beyond the common header are covered.
- The comments above each fixture document expected parse output; if fixture bytes are updated without comment updates, the documentation can drift.
- These tests are precise for union dispatch and flag decoding but do not cover bind, request, response, fault, or authenticated packet paths.
- The `CO_CANCEL` flag expectation intentionally excludes `FIRST` even though comments list individual flag meanings; this protects a subtle flag combination but could be misread during maintenance.

## Test signals
Passing subtests demonstrate correct `ncacn_packet` handling for the `co_cancel` and `orphaned` union cases and byte-stable round trips for minimal DCE/RPC packet headers.
