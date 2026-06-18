# sources/user-network-fs/samba/source4/torture/krb5/kdc-mit.c

## Purpose

`kdc-mit.c` is the MIT Kerberos counterpart to the Heimdal KDC torture tests. It validates AS-REQ packet shape, KDC reply sequences, PAC request handling, password and clock failures, reply KVNO semantics, and AES/RC4 enctype selection using MIT krb5 hook APIs.

## Important APIs, Types, and Functions

- `enum torture_krb5_test` selects plain, PAC, bad-password, clock-skew, AES, RC4, and AES+RC4 scenarios.
- `struct torture_krb5_context` keeps the torture context, MIT `krb5_context`, receive packet count, and decoded `krb5_kdc_req`/`krb5_kdc_rep`.
- External decode/free prototypes wrap MIT private-ish decode helpers for `krb5_error`, AS request/reply, and PA-DATA sequences.
- `torture_check_krb5_as_req()` validates outbound AS-REQ message type and requested keytype count.
- `torture_krb5_pre_send_test()` is installed with `krb5_set_kdc_send_hook()`.
- `torture_krb5_post_recv_test()` is installed with `krb5_set_kdc_recv_hook()` and validates KDC replies.
- `torture_krb5_as_req_creds()` configures credentials, optional PAC request, broken password, clock skew, and etype lists before `krb5_get_init_creds_password()`.
- `torture_krb5_init()` registers the MIT variant and `torture_krb5_canon_mit()`.

## Control Flow

`torture_krb5_init_context()` initializes Samba's MIT krb5 context and attaches send/receive hooks. On send, every scenario decodes the AS request and verifies it is a real `KRB5_AS_REQ` with keytypes. On receive, the packet counter drives expected responses. Plain authentication expects preauth required followed by an AS-REP. PAC request can see response-too-big before preauth and later a final response. Bad password and clock-skew scenarios expect their specific KDC errors. Enctype tests require a preauth reply first and then validate `as_rep->enc_part.enctype`.

The main credential flow builds a principal from the supplied Samba credentials, optionally configures MIT `krb5_get_init_creds_opt`, executes `krb5_get_init_creds_password()`, and asserts success or expected failure. PAC request registration is compiled only when `HAVE_KRB5_GET_INIT_CREDS_OPT_SET_PAC_REQUEST` is available.

## State and Persistence Behavior

There is no persistent state. Decoded request/reply pointers are transient and freed in the receive hook. The test mutates client context time for the clock-skew case and frees krb5 credential contents after successful authentication.

## Dependencies and Integration Points

The file depends on MIT krb5 hook support (`krb5_set_kdc_send_hook`, `krb5_set_kdc_recv_hook`), MIT decode/free functions, Samba Kerberos context helpers, command-line credentials, torture assertions, and build-time feature macros. `wscript_build` selects this file when `SAMBA4_USES_HEIMDAL` is false.

## Risks and Edge Cases

MIT behavior differs from Heimdal in response ordering, hook semantics, PA-DATA decoding, and optional PAC request support. The clock-skew test requires `kdc_timesync 0` in krb5 configuration. The PAC test is skipped for expected RODC cases because Windows behavior for non-cached users needs more investigation. Enctype tests assume MIT chooses the specific expected enctype from the configured list.

## Test Signals

Primary signals are successful `krb5.kdc` MIT tests for command-line AS-REQ, PAC request when compiled, bad password, clock skew, AES, RC4, AES+RC4, and canonicalization subtests. Failures in decoded message type, missing keytypes, wrong KDC error, wrong KVNO high bits, or wrong `enc_part.enctype` indicate regressions.
