# sources/user-network-fs/samba/source4/torture/krb5/kdc-heimdal.c

## Purpose

`kdc-heimdal.c` implements Samba torture tests for Kerberos AS-REQ behavior when Samba is built against Heimdal. It validates client/KDC packet sequences, PAC request handling, bad password and clock-skew failures, enctype negotiation for AES/RC4, RODC KVNO expectations, canonicalization-required behavior, and the "Orpheus' Lyre" style server-name mutation cases.

## Important APIs, Types, and Functions

- `enum torture_krb5_test` selects the scenario under test, including plain AS-REQ, PAC request, bad password, clock skew, AES, RC4, AES+RC4, and server-name mutation in requests/replies.
- `struct torture_krb5_context` tracks the torture context, target KDC address, packet counter, decoded `AS_REQ`/`AS_REP`, and optional `krb5-service`/`krb5-hostname` settings.
- `torture_krb5_pre_send_test()` decodes outbound `AS_REQ` packets and optionally rewrites the service principal in the request.
- `torture_check_krb5_error()` decodes `KRB_ERROR`, checks error codes, and can require PA-DATA such as `KRB5_PADATA_ENC_TIMESTAMP` and `KRB5_PADATA_ETYPE_INFO2`.
- `torture_check_krb5_as_rep_enctype()` decodes `AS_REP`, validates ticket version/KVNO, infers the expected reply enctype from PA-ENC-TIMESTAMP or requested etype order, and compares against an allowed list.
- `torture_krb5_post_recv_test()` validates the KDC reply sequence for each test and can rewrite the server name in an incoming `AS_REP`.
- `test_krb5_send_to_realm_override()` is installed with `smb_krb5_set_send_to_kdc_func()` to force TCP to the selected host and inspect/mutate both directions.
- `torture_krb5_as_req_creds()` builds credentials/options and drives `krb5_get_init_creds_password()`.
- `torture_krb5_init()` registers the `krb5.kdc` torture tests and the Heimdal canonicalization sub-suite.

## Control Flow

Initialization reads the `host` torture setting, resolves it as a numeric address, forces port 88, initializes a Samba Heimdal context, and installs `test_krb5_send_to_realm_override()`. Every AS credential acquisition then routes through the override: pre-send decodes or mutates `AS_REQ`, the real network exchange goes through `smb_krb5_send_and_recv_func_forced_tcp()`, and post-receive validates or mutates the reply before Heimdal continues processing.

The plain and PAC flows expect initial preauth-required replies, possible response-too-big handling, and then a valid `AS_REP`. Bad password expects `KRB5KDC_ERR_PREAUTH_FAILED`; clock skew expects `KRB5KRB_AP_ERR_SKEW`. Enctype tests constrain the client etype list and verify the encrypted reply matches the selected allowed enctype. If `kdc require canonicalization` is enabled, these tests expect `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN` because the client did not request canonicalization.

Server-name mutation has two directions. Outbound mutation changes `req_body.sname` to the configured service/hostname before sending, expecting bad integrity when a hostname is supplied. Inbound mutation rewrites the returned ticket server name to `bad/mallory` before the krb5 library consumes it.

## State and Persistence Behavior

The file does not write persistent state. It holds transient decoded ASN.1 packets in `struct torture_krb5_context` and frees them after validation. The destructor frees the resolved KDC address. It can mutate in-flight packet buffers, but those changes exist only for the test exchange.

## Dependencies and Integration Points

The test depends on Heimdal ASN.1 types/functions (`AS_REQ`, `AS_REP`, `KRB_ERROR`, `decode_*`, `ASN1_MALLOC_ENCODE`), Samba Kerberos helpers (`smb_krb5_init_context`, `smb_krb5_set_send_to_kdc_func`, `principal_from_credentials`), credentials from `samba_cmdline_get_creds()`, loadparm KDC canonicalization settings, and socket/address utilities. It is built into the `TORTURE_KRB5` module by `wscript_build` only when Heimdal is selected.

## Risks and Edge Cases

Packet-count assumptions are fragile across Kerberos library behavior changes, TCP fallback behavior, KDC response-too-big paths, and RODC caching. Enctype inference deliberately skips AES unless canonicalization is present because salt selection matters. Packet mutation touches allocated ASN.1 fields directly; ownership mistakes can leak or corrupt test state. Tests using clock skew depend on krb5 time handling and server configuration.

## Test Signals

Passing signals are successful `smbtorture krb5.kdc` cases: `as-req-cmdline`, `as-req-pac-request`, `as-req-break-pw`, `as-req-clock-skew`, `as-req-aes`, `as-req-rc4`, `as-req-aes-rc4`, and `as-req-change-server-{in,out,both}`. Strong negative signals are wrong KDC error codes, missing preauth PA-DATA, missing KVNO, unexpected RODC high KVNO bits, incorrect enctype, or successful authentication after deliberate server-name tampering.
