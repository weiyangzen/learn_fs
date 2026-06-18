<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh

## Purpose

This shell test provides `keyctl padd` useradd coverage for key creation with payloads read from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, expect_payload, keyutils_at_or_later_than, marker, md5sum_key, pcreate_key, pcreate_key_by_size, print_key, sleep, toolbox_report_result, unlink_key. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_big_key_type.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD USER KEY, PRINT PAYLOAD, ADD HEX USER KEY, PRINT PAYLOAD, UPDATE USER KEY, PRINT UPDATED PAYLOAD, UNLINK KEY, INCREASE QUOTA, ADD LARGE USER KEY, ADD SMALL BIG KEY, ADD HUGE BIG KEY, CLEAR KEYRING, RESET QUOTA.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh` preserves the expected behavior for `keyctl padd` useradd coverage for key creation with payloads read from stdin. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh -->
