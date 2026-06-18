# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_internal.h

## Purpose

This private header defines the raw Kerberos GENSEC state machine enum and per-context state structure shared by `gensec_krb5.c` and helper code.

## Important Types

`enum GENSEC_KRB5_STATE` defines `GENSEC_KRB5_SERVER_START`, `GENSEC_KRB5_CLIENT_START`, `GENSEC_KRB5_CLIENT_MUTUAL_AUTH`, and `GENSEC_KRB5_DONE`.

`struct gensec_krb5_state` stores the current state, `smb_krb5_context`, `krb5_auth_context`, encoded ticket `enc_ticket`, long-term `keyblock`, decoded `ticket`, whether fake GSSAPI wrapping is active, and AP request options.

## Control Flow

The enum controls `gensec_krb5_update_internal()`. Client instances start in `CLIENT_START`, emit AP-REQ, optionally wait in `CLIENT_MUTUAL_AUTH`, then reach `DONE`. Server instances start in `SERVER_START`, accept AP-REQ and produce AP-REP, then reach `DONE`. Any update after done is invalid.

## State And Persistence

The struct is allocated under the GENSEC security context and released by the destructor in `gensec_krb5.c`. It owns Kerberos objects that require provider-specific free functions. It stores enough ticket/key material to generate session info and verify PAC data after the handshake.

## Dependencies And Integration Points

It includes Samba and Kerberos headers and is used by the raw Kerberos implementation and helper inspection code. It connects the GENSEC state machine to Kerberos credentials, AP options, ticket parsing, PAC verification, session key extraction, and fake-GSS wrapping.

## Risks And Edge Cases

Ownership and state transitions are sensitive. If `state_position` is wrong, clients may skip mutual auth or servers may accept extra updates. If `keyblock` or `ticket` is missing after server authentication, PAC/session-info generation fails. If `gssapi` is incorrectly set, tokens may be wrapped or unwrapped in the wrong format and feature advertising changes.

## Test Signals

Good tests cover client and server state transitions, destructor cleanup after partial failures, fake-GSS and raw token paths, session-info access after done, and invalid update calls after completion.
