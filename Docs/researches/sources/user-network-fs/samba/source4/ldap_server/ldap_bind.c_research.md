# sources/user-network-fs/samba/source4/ldap_server/ldap_bind.c

## Purpose

`ldap_bind.c` implements LDAP Bind and Unbind handling. It supports simple binds, SASL/GENSEC binds, SASL sign/seal stream wrapping, strong-auth policy, TLS channel bindings, backend reinitialization under authenticated credentials, and Unbind disconnect.

## Important APIs, Types, and Functions

Exported entry points are `ldapsrv_BindRequest()` and `ldapsrv_UnbindRequest()`. Internal paths include `ldapsrv_BindSimple()`, `ldapsrv_BindSimple_done()`, `ldapsrv_BindSASL()`, `ldapsrv_BindSASL_done()`, `ldapsrv_setup_gensec()`, SASL postprocess helpers, bind wait helpers, and unbind wait helpers.

## Control Flow

Simple bind enforces strong-auth transport rules, starts asynchronous simple authentication, then on completion replaces `conn->session_info`, drops the old LDB, reinitializes the backend, and queues `BindResponse`. SASL bind starts a GENSEC mechanism, feeds secblobs until complete, handles continuation responses, enforces sign/seal or TLS requirements, optionally creates a GENSEC tstream, and schedules stream replacement after the success response is written. Unbind removes pending calls and returns a local-disconnect wait status.

## State and Persistence Behavior

Bind mutates `conn->gensec`, `conn->session_info`, `conn->ldb`, `conn->authz_logged`, `conn->limits.expire_time`, and possibly `conn->sockets.sasl` and `active`. It does not directly persist directory data but changes authorization for subsequent backend operations.

## Dependencies and Integration Points

It depends on Samba auth, GENSEC, `gensec_tstream`, TLS channel bindings, loadparm strong-auth policy, LDB errors, tevent NTSTATUS helpers, and wait/postprocess hooks consumed by `ldap_server.c`.

## Risks and Edge Cases

Bind returns `LDAP_BUSY` when pending calls exist. Strong-auth compatibility modes affect channel-binding and TLS requirements. SASL sign/seal is refused over TLS or when SASL encryption is already active. RFC 4513 cancellation of in-progress SASL on a new bind is still TODO. Windows-compatible DSID/data diagnostics are client-visible.

## Test Signals

Signals include simple bind success/failure, simple bind without TLS under strong auth, SASL multi-leg flows, bad channel bindings, sign/seal stream activation, SASL-over-TLS refusal with sign/seal, backend init failure, `LDAP_BUSY`, Unbind disconnect, and GENSEC expiry propagation.
