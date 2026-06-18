# sources/user-network-fs/samba/source4/torture/ndr/lsa.c

## Purpose

`lsa.c` is a Samba local torture suite for validating generated NDR pull behavior for LSA RPC request and response structures. It is fixture-driven: each static byte array captures an on-the-wire NDR blob, and each typed check function asserts that the generated `ndr_lsa` decoder reconstructs the expected `struct lsa_*` fields. The suite covers policy open calls, name/SID lookup variants, account and secret object operations, trusted-domain creation and update paths, privilege enumeration, and forest-trust information calls.

## Important APIs, types, and functions

The file depends on the shared NDR torture macros from `torture/ndr/ndr.h`, especially `torture_suite_add_ndr_pull_fn_test`, which wraps a generated pull routine such as `ndr_pull_lsa_OpenPolicy` with a fixture, flags, and a typed check callback. The test types are generated LSA RPC structures from `librpc/gen_ndr/ndr_lsa.h` through the local include graph. Important local callbacks include `lsarlookupnames_in_check`, `lsarlookupnames_out_check`, `lsarlookupsids_in_check`, `lsarlookupsids_out_check`, `lsaropenpolicy*_check`, secret callbacks for `lsa_CreateSecret`, `lsa_OpenSecret`, `lsa_SetSecret`, `lsa_QuerySecret`, lookup callbacks for `lsa_LookupSids2`, `lsa_LookupNames2`, `lsa_LookupNames3`, `lsa_LookupSids3`, and trust callbacks for `lsa_lsaRSetForestTrustInformation` and `lsa_SetTrustedDomainInfoByName`.

`ndr_lsa_suite(TALLOC_CTX *ctx)` is the integration entry point. It creates the `"lsa"` torture suite and registers each fixture in explicit order, usually as separate `NDR_IN` and `NDR_OUT` tests for the same RPC.

## Control flow

There is no runtime protocol state machine in this file. Control flow is registration-time and test-run-time only. At registration, `ndr_lsa_suite` allocates a suite, registers one tcase per RPC direction through the helper macro, and returns the suite to the higher-level local NDR aggregator. At execution time, the shared wrapper initializes an `ndr_pull` context over the fixture blob, applies the supplied NDR direction flag, decodes into a zeroed generated structure, verifies that all fixture bytes were consumed, then invokes the typed check callback.

The callbacks are field assertions. The name/SID lookup tests check bulk counts, reference-domain lists, translated name/SID arrays, lookup levels, lookup options, client revisions, and NTSTATUS results. Policy and object operation tests check object attributes, access masks, handles only superficially, secret value pointer layout, resume handles, and returned status. Forest-trust tests check record counts, record types, domain names, NetBIOS names, SIDs, trust direction/type/attributes, POSIX offset, auth blob sizing, and check-only behavior.

## State and persistence

All state is embedded in immutable static fixture arrays plus stack-local expected values. The suite does not modify databases, network services, files, or persistent Samba state. Handles in the fixture blobs are decoded as opaque values, but most handle validation is marked as `FIXME`, so the tests use them primarily to preserve byte layout around later fields. Memory ownership is delegated to the shared torture/NDR wrappers using talloc contexts.

## Dependencies

The file depends on Samba torture assertions, generated LSA NDR routines and structures, common SID/GUID helpers such as `dom_sid_parse_talloc`, and the shared local NDR test harness. It also depends on generated constants such as `LSA_TRUST_TYPE_UPLEVEL` and `LSA_TRUSTED_DOMAIN_INFO_FULL_INFO_INTERNAL`.

## Integration points

`ndr_lsa_suite` is included by `torture_local_ndr` in `ndr.c`, making these LSA fixtures part of the local `ndr` torture command. The test suite is therefore a regression guard for changes in LSA IDL, generated NDR code, pointer layout, conformant/varying arrays, string decoding, SID decoding, and RPC direction-specific structure annotations.

## Risks

Several checks are intentionally incomplete. Comments mark missing validation for policy and object handles, some SIDs, returned secret modification times, and query-forest-trust payload contents. `lsa_LookupSids3` has an output fixture and check function, but its `NDR_OUT` test registration is commented out, leaving that path unexecuted. The suite mostly tests successful decode/status cases and does not exercise malformed LSA payloads. Large repeated lookup fixtures with 100 names/SIDs are useful for array coverage, but many per-entry values are not deeply validated.

## Test signals

Strong signals are full fixture-byte consumption enforced by the harness, exact count and pointer-nullability checks, expected domain/name strings such as `BUILTIN`, `NT AUTHORITY`, `Account Operators`, and `Administrators`, expected status success for many responses, and forest-trust field checks including `f1.test`, `F1`, and a parsed domain SID. Weak signals are the `FIXME` assertions and unregistered output paths.
