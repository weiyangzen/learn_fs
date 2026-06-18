# sources/user-network-fs/libsmb2/lib/ntlmssp.h

## Purpose

`ntlmssp.h` declares libsmb2's NTLMSSP authentication interface used by SMB2 session setup in both client and server modes. It hides `struct auth_data` internals and exposes blob generation, authentication verification, SPNEGO wrapping controls, message-type parsing, and session-key extraction.

## Important APIs, Types, And Functions

The header defines NTLMSSP message constants `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, and `AUTHENTICATION_MESSAGE`, forward-declares `struct auth_data`, and declares `ntlmssp_init_context`, `ntlmssp_destroy_context`, `ntlmssp_set_spnego_wrapping`, `ntlmssp_get_spnego_wrapping`, `ntlmssp_get_message_type`, `ntlmssp_generate_blob`, `ntlmssp_authenticate_blob`, `ntlmssp_get_authenticated`, and `ntlmssp_get_session_key`.

## Control Flow

Callers create an auth context with user/password/domain/workstation/client-challenge data, optionally set SPNEGO wrapping, then exchange blobs through `ntlmssp_generate_blob`. Server session setup can call `ntlmssp_authenticate_blob` directly or via `ntlmssp_generate_blob` handling of an authentication message, then query authenticated state and session key. `ntlmssp_get_message_type` is used to detect raw or SPNEGO-wrapped NTLMSSP tokens before choosing the auth path.

## State And Persistence Behavior

The header exposes an opaque heap-owned context lifetime: `ntlmssp_init_context` allocates it, `ntlmssp_destroy_context` releases it, and `ntlmssp_get_session_key` returns a newly allocated key buffer to the caller. There is no persistent storage contract in the header.

## Dependencies And Integration Points

The header includes optional `config.h`, defines `_GNU_SOURCE`, supports C++ linkage, and references `struct smb2_context` and `struct smb2_server` types supplied by libsmb2 internal headers in including translation units. Its main integration is `libsmb2.c` session setup.

## Risks And Edge Cases

The API requires callers to manage ownership carefully: output blobs point at `auth_data` internal storage, while session keys are separately allocated for the caller. `client_challenge` is typed as `const char *` but semantically must point to at least eight binary bytes. The header name guard `_GSSAPI_WRAPPER_H_` does not match the NTLMSSP header name, which can confuse maintainers and risks collision with an actual GSSAPI wrapper guard.

## Test Signals

Compile tests should include C and C++ consumers and all security configurations. API tests should verify context creation/destruction, SPNEGO flag round trips, raw and wrapped message-type parsing, blob exchange sequencing, authenticated-state reporting, and ownership of returned session keys.
