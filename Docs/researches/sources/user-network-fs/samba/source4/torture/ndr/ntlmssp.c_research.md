# sources/user-network-fs/samba/source4/torture/ndr/ntlmssp.c

## Purpose

`ntlmssp.c` validates generated NDR parsing for NTLMSSP negotiate, challenge, and authenticate messages. It checks header signatures, message types, security-buffer lengths, flags, version fields, AV pair lists, NTLMv2 response internals, identity strings, and session-key payloads. Negotiate and challenge fixtures are also registered for pull/push byte validation.

## Important APIs, types, and functions

The file includes generated `librpc/gen_ndr/ndr_ntlmssp.h` and the shared NDR torture header. Important generated structures are `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, `AUTHENTICATE_MESSAGE`, `NTLMv2_RESPONSE`, and `AV_PAIR_LIST`. Local callbacks are `ntlmssp_NEGOTIATE_MESSAGE_check`, `ntlmssp_CHALLENGE_MESSAGE_check`, and `ntlmssp_AUTHENTICATE_MESSAGE_check`. `ndr_ntlmssp_suite(TALLOC_CTX *ctx)` registers the suite.

## Control flow

The suite first registers pull-only tests for all three message types. It then registers validate tests for `NEGOTIATE_MESSAGE` and `CHALLENGE_MESSAGE`, which adds push-back byte comparison for those two fixtures. The authenticate fixture is pull-only, likely because the message is more complex and may not be byte-stable under the encoder.

## State and persistence

There is no mutable state. Expected binary values for server challenge, reserved bytes, LM response, NTLMv2 response, client challenge, machine ID, channel bindings, and encrypted random session key are local arrays. Decoded AV pair lists are copied from nested decoded fields into stack variables for assertion.

## Dependencies

Dependencies include generated NTLMSSP NDR routines and constants, NTLMSSP version constants, AV pair identifiers, the shared local NDR harness, and Samba torture assertions.

## Integration points

`ndr_ntlmssp_suite` is registered by `torture_local_ndr` in `ndr.c`. It protects generated parsing for NTLMSSP tokens used by SMB authentication and SPNEGO negotiation paths.

## Risks

The authenticate message is not registered as a validate test, so encoder byte stability for that complex structure is not checked here. Cryptographic correctness is not tested; the suite asserts parsed bytes and fields, not that responses verify against passwords or challenges. Timestamp interpretation is left as a comment. The coverage is limited to one captured negotiate, challenge, and authenticate sequence.

## Test signals

Strong signals include `"NTLMSSP"` signature checks, message type discriminants, negotiate flag values, null domain/workstation handling, target name and target info parsing, AV pair count and per-pair names/lengths, NTLMv2 response fields, `MsvAvSingleHost` token info and machine ID, channel bindings, target name, domain/user/workstation strings, encrypted session key bytes, version fields, full fixture consumption, and byte-identical validation for negotiate and challenge messages.
