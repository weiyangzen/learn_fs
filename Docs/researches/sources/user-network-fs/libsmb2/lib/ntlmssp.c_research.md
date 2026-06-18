# sources/user-network-fs/libsmb2/lib/ntlmssp.c

## Purpose

`ntlmssp.c` implements NTLMSSP authentication blob generation, parsing, and verification for libsmb2 client and server modes. It generates NTLM negotiate, challenge, and authenticate messages, optionally wraps/unwraps them in SPNEGO, derives NTLMv2 responses and exported session keys, and verifies client authenticate blobs on the server side.

## Important APIs, Types, And Functions

The central private type is `struct auth_data`, which stores the current output buffer, parsed NTLM challenge copy, user/domain/password/workstation strings, target name/info, client and server challenges, SPNEGO wrapping flag, authentication result, timestamp, and exported session key.

Public functions include `ntlmssp_init_context`, `ntlmssp_destroy_context`, `ntlmssp_set_spnego_wrapping`, `ntlmssp_get_spnego_wrapping`, `ntlmssp_get_authenticated`, `ntlmssp_generate_blob`, `ntlmssp_authenticate_blob`, `ntlmssp_get_session_key`, and `ntlmssp_get_message_type`. `ntlmssp_get_utf16_field` is externally visible in the C file but not declared in the header.

Important private helpers include `encoder` for append-only output buffer construction, `encode_ntlm_negotiate_message`, `ntlm_decode_challenge_message`, `ntlm_convert_password_hash`, `NTOWFv1`, `NTOWFv2`, `encode_temp`, `encode_ntlm_auth`, and `encode_ntlm_challenge`.

## Control Flow

Client-side generation starts with `ntlmssp_generate_blob` receiving `input_buf == NULL`, which emits a negotiate message and optionally SPNEGO-wraps it. When a challenge blob arrives, `ntlmssp_get_message_type` unwraps SPNEGO if needed and identifies the NTLMSSP message type. For a challenge, `ntlm_decode_challenge_message` copies selected challenge fields, appends a target-name AV pair, and stores target info. If no domain was configured, the target name can become the SMB2 domain and trigger password lookup from file. `encode_ntlm_auth` then computes the NTLMv2 response using `NTOWFv2`, the server challenge, timestamp, client challenge, and target info; builds an authenticate message with domain/user/workstation fields; and stores the exported session key.

Server-side generation receives a negotiate message and calls `encode_ntlm_challenge`, which emits a challenge message, target info, timestamp, and server challenge. When an authenticate message arrives, `ntlmssp_generate_blob` calls `ntlmssp_authenticate_blob`, marks `is_authenticated` based on the verification result, and optionally emits a SPNEGO auth result.

Verification in `ntlmssp_authenticate_blob` parses UTF-16 domain/user/workstation fields, updates the SMB2 context identity, asks `server->handlers->authorize_user` for authorization/password data, supports anonymous if allowed, extracts the NTLMv2 response and temp blob, recomputes `ResponseKeyNT` and `NTProofStr`, compares it to the response, derives the exported session key, and wipes the SMB2 password after use.

## State And Persistence Behavior

`auth_data` owns heap buffers and strings for the lifetime of an authentication exchange. `encoder` grows `auth_data->buf` geometrically and appends protocol fields. The exported session key remains in `auth_data->exported_session_key` until copied by `ntlmssp_get_session_key`, which allocates a fresh key buffer for the caller. Server verification writes user/domain/workstation into the `smb2_context`, and clears the password string after computing the proof. No disk persistence is performed directly, though client generation can call `smb2_set_password_from_file` after learning a domain.

## Dependencies And Integration Points

The file depends on endian helpers, UTF-16 conversion, SMB2 time conversion, SMB2 context setters, SPNEGO wrapper functions, MD4, MD5, and HMAC-MD5. It integrates tightly with `libsmb2.c` session setup: client negotiation calls `ntlmssp_generate_blob` for outgoing tokens and `ntlmssp_get_session_key` for signing/encryption keys; server session setup calls `ntlmssp_get_message_type`, `ntlmssp_generate_blob`, `ntlmssp_get_authenticated`, and `ntlmssp_get_session_key`.

## Risks And Edge Cases

This is security-sensitive code. The server challenge in `encode_ntlm_challenge` is deterministic bytes `1..8`, which is unsuitable for real authentication because NTLM challenges must be unpredictable to prevent replay/precomputation attacks. `ntlmssp_init_context` unconditionally copies eight bytes from `client_challenge`, so callers must never pass NULL. Several challenge parsing paths perform partial bounds checks but still rely on offsets from untrusted blobs; malformed SPNEGO/NTLM inputs need fuzzing, especially target-name and target-info offsets.

The code uses MD4 and MD5/HMAC-MD5 because NTLM requires them; they should not be generalized. Endian conversions in some parse paths use host-to-little macros where little-to-host would be clearer, which is harmless on little-endian but risky on big-endian. The `ntlm:` password-hash shortcut validates only length/prefix and then converts hex characters without rejecting non-hex input. Password and key material is partly cleared (`smb2_set_password(smb2, "")`, context frees), but not all temporary arrays are explicitly zeroized.

SPNEGO wrapping state is inferred from incoming blobs and carried in `auth_data->spnego_wrap`; mismatches between wrapped and raw tokens can break negotiation. Anonymous behavior depends on server policy and empty user/password semantics. `ntlmssp_get_utf16_field` checks the descriptor offset but not that `field_off + field_len` stays within `input_len`, creating a malformed-input risk.

## Test Signals

Client tests should cover raw NTLMSSP and SPNEGO-wrapped negotiate/challenge/authenticate flows, configured domain versus domain learned from challenge target name, password-file lookup after domain discovery, anonymous auth, `ntlm:<hash>` credentials, and exported session-key use for SMB signing. Server tests should cover handler authorization success/failure, anonymous allowed/disallowed, malformed authenticate fields, wrong password proof, and session key extraction. Security tests should require random server challenges before production server use. Fuzz tests should target `ntlmssp_get_message_type`, `ntlm_decode_challenge_message`, `ntlmssp_get_utf16_field`, and `ntlmssp_authenticate_blob` with truncated and offset-corrupt blobs.
