# sources/user-network-fs/samba/source4/auth/gensec/gensec_gssapi.h

## Purpose

This header exposes the private state layout for the GSSAPI GENSEC implementation. It is kept visible enough for tests, especially RPC/PAC tests, to inspect the PAC-related GSSAPI context state.

## Important APIs, Types, And Constants

`enum gensec_gssapi_sasl_state` defines the negotiation stages: `STAGE_GSS_NEG`, `STAGE_SASL_SSF_NEG`, `STAGE_SASL_SSF_ACCEPT`, and `STAGE_DONE`. `NEG_SEAL`, `NEG_SIGN`, and `NEG_NONE` encode SASL security-layer choices.

`struct gensec_gssapi_state` is the central per-security-context state. It stores `gssapi_context`, imported `server_name` and accepted `client_name`, wanted/got GSS flags, delegated credential handle, expiry time, selected GSS OID, channel-binding structures, Samba Kerberos context, client/server GSS credential containers, SASL enablement and state, negotiated SASL protection, max wrap size, exchange count, cached signature size, and target principal.

## Control Flow

The header has no executable flow, but the enum drives `gensec_gssapi_update_internal()` in `gensec_gssapi.c`. Normal GSS negotiation progresses from `STAGE_GSS_NEG` to `STAGE_DONE`; SASL mode progresses from `STAGE_GSS_NEG` to `STAGE_SASL_SSF_NEG`, then on the server to `STAGE_SASL_SSF_ACCEPT`, and finally to `STAGE_DONE`.

## State And Persistence

All fields are in-memory and talloc-owned through the associated `gensec_security` object. GSS handles must be released by the C file destructor. `max_wrap_buf_size`, `sasl_protection`, `gss_got_flags`, and `sig_size` are cached negotiation results that later wrap/sign/seal calls trust.

## Dependencies And Integration Points

The type uses GSSAPI types (`gss_ctx_id_t`, `gss_name_t`, `gss_cred_id_t`, `gss_OID`, channel bindings), Samba `NTTIME`, `smb_krb5_context`, and `gssapi_creds_container`. It is included by the implementation and test code that needs direct inspection.

## Risks And Edge Cases

Because this is a private-but-visible state structure, field changes can break tests or any internal code that inspects it. Negotiation correctness depends on the enum and bit constants matching the C implementation. Stale cached `sig_size` or mismatched SASL protection bits would affect subsequent packet sizing and security decisions.

## Test Signals

Tests should inspect stage transitions, negotiated `sasl_protection`, `gss_got_flags`, selected OID, channel binding pointer setup, delegated credential transfer, and cached wrap/sign sizing after successful GSSAPI and SASL handshakes.
