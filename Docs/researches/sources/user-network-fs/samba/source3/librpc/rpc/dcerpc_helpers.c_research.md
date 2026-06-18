# sources/user-network-fs/samba/source3/librpc/rpc/dcerpc_helpers.c

## Purpose
`dcerpc_helpers.c` implements source3 helper routines for encoding DCERPC packets, calculating authenticated fragment sizes, appending GENSEC-backed auth footers, and validating incoming auth trailers.

## Important APIs, types, and functions
- `dcerpc_push_ncacn_packet()` fills standard DCERPC header fields, NDR-encodes the packet, sets `frag_length`, and optionally prints debug NDR.
- `dcerpc_push_dcerpc_auth()` NDR-encodes the authentication trailer header with credentials.
- `dcerpc_guess_sizes()` computes max stub data, fragment length, auth token length, and pad length for unauthenticated and authenticated auth levels.
- `add_generic_auth_footer()` signs or seals the data portion using GENSEC.
- `get_generic_auth_footer()` checks or unseals incoming data using GENSEC.
- `dcerpc_add_auth_footer()` appends padding, an empty auth trailer header, then appends the generated signature/seal blob.
- `dcerpc_check_auth()` validates trailer type/level/context, verifies/decrypts credentials, strips padding, and updates trailer data.

## Control flow
Outgoing packets are sized first. For no/connect auth without auth tokens, size is header plus data. For packet/integrity/privacy, the code reserves the auth trailer, gets a GENSEC signature size for aligned data, reduces data length accordingly, and computes pad length. When adding a footer, it appends pad bytes, marshals a trailer with empty credentials so the header is included in signatures, then signs or seals and appends the auth blob.

Incoming auth first accepts unauthenticated and connect-level packets with no auth length. Authenticated packets must have a trailer; the code pulls it, checks type/level/context ID against `pipe_auth_data`, calculates the signed/encrypted data portion and full packet excluding credentials, then delegates check/unseal to GENSEC. Privacy mode copies decrypted data back into the trailer copy and strips auth padding.

## State and persistence behavior
No persistent state exists. Runtime state is in `pipe_auth_data` and its `gensec_security` context. Blob ownership is talloc-based, and `auth_info.credentials` is freed after use.

## Dependencies and integration points
The file depends on generated DCERPC NDR, `dcerpc_internal.h`, GENSEC, and GSE headers. It is used by DCERPC client/server transport code to apply NTLMSSP/Kerberos/SPNEGO/SCHANNEL packet protection uniformly.

## Risks and edge cases
Fragment size math is security-critical: underflow on small `max_xmit_frag`, mismatched padding, or wrong signature size can corrupt packets. Auth trailer validation must reject mismatched auth type, level, and context ID. Privacy mode mutates data in place, so callers must handle blob ownership correctly. Auth levels `PACKET` and `INTEGRITY` are treated the same for signing.

## Test signals
Test no/connect/integrity/privacy paths, max fragment boundaries, pad lengths 0..15, GENSEC signature-size failure, mismatched trailer fields, truncated auth trailers, privacy decrypt copyback, and round trips with Kerberos, NTLMSSP, SPNEGO, and SCHANNEL contexts.
