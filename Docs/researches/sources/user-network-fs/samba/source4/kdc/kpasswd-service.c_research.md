## sources/user-network-fs/samba/source4/kdc/kpasswd-service.c

Purpose: common kpasswd packet processor. It parses the outer kpasswd framing, accepts the AP-REQ with Samba GENSEC Kerberos, unwraps the encrypted password payload, calls the backend-specific `kpasswd_handle_request()`, wraps the response, and emits the RFC-style reply frame.

Important APIs and functions: `kpasswd_process()` is the sole exported implementation. It validates RODC forwarding (`kdc->am_rodc` returns `KDC_PROXY_REQUEST`), source/destination socket addresses, request length/version/AP-REQ boundaries, server credentials for `kadmin/changepw`, keytab binding through `kdc->kpasswd_keytab_name`, GENSEC local/remote addresses, `gensec_update()`, `gensec_unwrap()`, `kpasswd_handle_request()`, `gensec_wrap()`, `kpasswd_make_error_reply()`, and `smb_krb5_mk_error()` for unauthenticated Kerberos error bodies.

Control flow: after frame validation, the function constructs explicit `kadmin/changepw` credentials bound to the KDC krb5 context so the loaded KDB/DSDB plugin is used. AP-REQ failure and unwrap/wrap failures move to the reply path with kpasswd hard-error semantics. Handler failures clear the AP-REP and generate a Kerberos error with a kpasswd error blob. Success returns a header with AP-REP length and encrypted response body.

State and persistence: no persistence is performed here. All per-request buffers are under `tmp_ctx`; the caller receives a talloced reply. Credentials deliberately reuse `kdc->smb_krb5_context` to avoid opening a separate database context.

Dependencies and integration: sits between the KDC server network layer, tsocket address handling, Samba credentials, GENSEC Kerberos, `kpasswd-helper`, and MIT/Heimdal-specific `kpasswd_handle_request()` implementations selected at build time.

Risks: frame-length arithmetic is security sensitive; `enc_data_len` includes the header-derived layout and must not underflow. The explicit realm/principal setup prevents match-by-key fallback, so regressions could permit accepting the wrong key. MIT sets the remote address while Heimdal deliberately skips it due to krb5_rd_req behaviour.

Test signals: truncated frames, mismatched total length, unsupported versions, invalid addresses, AP-REQ failures, unwrap/wrap errors, RODC proxying, and successful version 1/RFC3244 round trips.
