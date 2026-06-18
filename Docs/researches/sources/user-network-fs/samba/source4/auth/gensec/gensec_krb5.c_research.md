# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.c

## Purpose

This file implements Samba's raw Kerberos GENSEC backend plus a disabled fake-GSSAPI Kerberos wrapper mode used for compatibility. It creates AP-REQ/AP-REP tokens with the Kerberos library, accepts raw Kerberos tickets from clients, exposes session keys and PAC-backed session information, supports `krb5_mk_priv` sealing for the raw mode, and registers the `krb5` and `fake_gssapi_krb5` GENSEC mechanisms.

## Important APIs, Functions, And State

The public entry point is `gensec_krb5_init(TALLOC_CTX *ctx)`. Major internal functions include `gensec_krb5_start()`, server/client start wrappers, `gensec_krb5_common_client_creds()`, `gensec_gssapi_gen_krb5_wrap()`, `gensec_gssapi_parse_krb5_wrap()`, `gensec_krb5_update_internal()`, update send/recv wrappers, `gensec_krb5_session_key()`, Heimdal and MIT variants of `gensec_krb5_session_info()`, `gensec_krb5_wrap()`, `gensec_krb5_unwrap()`, `gensec_krb5_have_feature()`, and `gensec_krb5_final_auth_type()`.

State is `struct gensec_krb5_state` from `gensec_krb5_internal.h`: state-machine position, Samba Kerberos context, Kerberos auth context, encoded ticket, long-term keyblock for PAC verification, decoded ticket, fake-GSSAPI flag, and AP-REQ options.

## Control Flow

Startup obtains credentials from GENSEC, allocates state, fetches or creates a Kerberos context through credentials, initializes a `krb5_auth_context`, enables sequence handling, translates optional local and remote tsocket addresses into Kerberos addresses, and stores them on the auth context.

Client start rejects missing hostnames, IP addresses, and `localhost`, then sets `GENSEC_KRB5_CLIENT_START`, `AP_OPTS_USE_SUBKEY`, and optional mutual authentication. `gensec_krb5_common_client_creds()` acquires a ccache, optionally installs Heimdal event routing, and builds an AP-REQ either for an explicit parsed target principal with `krb5_get_credentials()`/`krb5_mk_req_extended()` or for service/hostname with `krb5_mk_req()`.

`gensec_krb5_update_internal()` is the handshake state machine. In client-start state it emits the encoded ticket, optionally wrapped as a GSS Kerberos application token, and either finishes or waits for mutual auth. In mutual-auth state it unwraps an AP-REP if fake-GSSAPI mode is active and validates it with `krb5_rd_rep()`. In server-start state it obtains a keytab, derives or nulls the acceptor principal based on credential specificity and password-backed keytabs, unwraps optional fake-GSS tokens, calls `smb_krb5_rd_req_decoded()`, stores decoded ticket and keyblock, emits AP-REP raw or wrapped, and moves to done.

Session info differs by Kerberos provider. Heimdal uses `krb5_ticket_get_client()` and `krb5_ticket_get_authorization_data_type()`. MIT copies `ticket->enc_part2->client` and finds PAC authdata via `krb5_find_authdata()`. Both decode and verify the PAC with the stored long-term keyblock, call `gensec_generate_session_info_pac()`, and attach the Kerberos session key.

## State And Persistence

All state is per-handshake memory under `gensec_security`. The destructor frees encoded tickets, decoded tickets, keyblocks, and auth contexts. Credentials, ccache, keytab, ticket, keyblock, auth context sequence numbers, and AP options persist only while the GENSEC object is live. There is no disk persistence beyond Kerberos libraries' normal ccache/keytab usage.

## Dependencies And Integration Points

The implementation depends on Samba credentials, Kerberos wrappers, PAC utilities, ASN.1 helpers for fake-GSS wrapping, GENSEC registration, tevent, tsocket, DCE/RPC constants, and `smb_krb5_rd_req_decoded()` from the Heimdal/MIT compatibility files. It integrates with `auth.h` through session-info generation, with Kerberos credentials/keytab/ccache providers, and with GENSEC feature probing for session key/sign/seal.

## Risks And Edge Cases

Risk areas include hostname validation, address binding failures, ccache and KDC error mapping, fake-GSS wrapper parsing accepting malformed tokens, mutual-auth state handling, provider-specific ticket/PAC access, keytab principal matching behavior, long-term key selection for PAC verification, and feature advertising. Raw `krb5` reports signing/sealing through `krb5_mk_priv`, while fake-GSSAPI mode disables sign/seal features; callers must select the correct mechanism.

## Test Signals

Useful tests cover client AP-REQ generation with explicit principal and service/hostname, server AP-REQ acceptance with keytab principal and match-by-key paths, fake-GSS wrapper encode/decode, mutual authentication success and failure, ccache/KDC error mapping, PAC present and absent session info, MIT and Heimdal builds, session key extraction after done state, wrap/unwrap seal behavior, and feature flags for raw versus fake-GSS mode.
