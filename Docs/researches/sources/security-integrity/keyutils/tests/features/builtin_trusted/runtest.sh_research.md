<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh -->
# sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh

## Purpose

This shell test provides feature coverage for the `builtin_trusted` keyutils/kernel capability. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: a4aadc8d, a9293377, ac4306b7, bc38ae82, be30f90c, create_key, d0e9cbce, d4e93686, d867638a, d976c1b4, da73b7cd, e8ab87d0, eeca00ec, expect_error, expect_keyring_rlist, f589d945, f6fae4b5, f70d0101, and 5 more helpers. Expected errno assertions are: EACCES, ENOKEY, EOPNOTSUPP. Capability or environment gates are: have_public_key.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: FIND BUILTIN TRUSTED KEYRINGS, TRY ADDING USER KEYS, TRY ADDING ASYMMETRIC KEYS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh` preserves the expected behavior for feature coverage for the `builtin_trusted` keyutils/kernel capability. The explicit expected errors (`EACCES, ENOKEY, EOPNOTSUPP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh -->
