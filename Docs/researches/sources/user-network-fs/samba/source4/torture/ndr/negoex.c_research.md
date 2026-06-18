# sources/user-network-fs/samba/source4/torture/ndr/negoex.c

## Purpose

`negoex.c` validates generated NDR decoding and re-encoding for a NEGOEX message array containing two messages. The fixture represents a NEGOEX acceptor negotiation message followed by acceptor metadata, including the shared signature, message headers, conversation ID, auth-scheme GUID, and metadata exchange blob.

## Important APIs, types, and functions

The file includes generated `librpc/gen_ndr/ndr_negoex.h` plus the shared NDR torture header. `negoex_MESSAGE_ARRAY_check` validates `struct negoex_MESSAGE_ARRAY` and local copies of `struct negoex_MESSAGE`. It uses `GUID_from_string` and `torture_assert_guid_equal` for stable GUID comparisons. `ndr_negoex_suite(TALLOC_CTX *ctx)` registers the fixture with `torture_suite_add_ndr_pull_validate_test`, so the shared harness performs both decode checks and push-back byte comparison.

## Control flow

The suite has one fixture. The shared harness decodes `negoex_MESSAGE_ARRAY_data` as a `negoex_MESSAGE_ARRAY`, asserts full fixture consumption, calls `negoex_MESSAGE_ARRAY_check`, then re-encodes and compares the bytes. The check function asserts an array count of two, validates message 0 as `NEGOEX_MESSAGE_TYPE_ACCEPTOR_NEGO`, and message 1 as `NEGOEX_MESSAGE_TYPE_ACCEPTOR_META_DATA`.

## State and persistence

There is no mutable state outside stack-local expected GUIDs. Both decoded messages are copied into a stack `struct negoex_MESSAGE m` for easier assertion. The metadata exchange payload is not parsed by this test beyond length.

## Dependencies

Dependencies are generated NEGOEX NDR routines and constants, the shared local NDR harness, GUID parsing helpers, and Samba torture assertions.

## Integration points

`ndr_negoex_suite` is added by `torture_local_ndr` in `ndr.c`. It protects generated NEGOEX parser and encoder behavior for SPNEGO extension negotiation payloads.

## Risks

The first message's random value is not asserted; a commented assertion hints that the random blob should be checked but is not represented in a convenient scalar form. The second message's metadata exchange blob is only checked for length, not content. Only one two-message sequence is covered, so initiator message types, alerts, verify messages, malformed lengths, and alternate extension counts are outside this file's coverage.

## Test signals

Strong signals include array count, exact `"NEGOEXTS"` signatures, message types, sequence numbers, header/message lengths, shared conversation ID, auth-scheme GUID, zero extension count in the negotiation message, metadata auth-scheme GUID, exchange blob length, full fixture consumption, and byte-identical push validation.
