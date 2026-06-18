# File Research: sources/virtualization/nbdkit/server/crypto.c

Purpose: Implements TLS initialization, certificate/PSK credential loading, connection upgrade to GnuTLS, TLS-wrapped transport I/O, TLS debug reporting, and public peer-certificate DN helpers.

Build modes:
- With `HAVE_GNUTLS`, full TLS support is compiled.
- Without GnuTLS, `crypto_init` rejects enabled TLS and public TLS peer-DN helpers report unsupported-platform errors.

Credential loading:
- X.509 mode looks for `ca-cert.pem`, optional `ca-crl.pem`, and server key/cert pairs in configured/default certificate directories.
- It supports the primary `server-cert.pem`/`server-key.pem` plus numbered `server-cert-N.pem`/`server-key-N.pem` pairs.
- Default certificate search depends on privilege: non-root checks user pki/config paths; root checks `root_tls_certificates_dir`.
- `--tls-psk` selects PSK credentials instead of certificates and resolves the PSK file to an absolute path.

Initialization:
- `crypto_init(tls_set_on_cli)` calls `gnutls_global_init`, chooses PSK or X.509 auth, and enforces `--tls=require`.
- If TLS was explicitly requested as `on` but credentials cannot load, it warns and disables TLS.
- `crypto_free` releases active credential objects and calls `gnutls_global_deinit`.

Connection upgrade:
- `crypto_negotiate_tls(sockin, sockout)` creates a server session, attaches credentials, configures priority, sets transports, runs the handshake, logs session details when enabled, then swaps `conn->recv`, `conn->send`, and `conn->close` to TLS implementations.
- Certificate mode can request/verify client certs when `tls_verify_peer` is set.
- PSK mode extends the priority string with PSK key-exchange algorithms.

TLS I/O:
- `crypto_recv` mirrors raw receive semantics: complete read, clean EOF before bytes, or error/partial-record failure.
- `crypto_send` uses GnuTLS corking/uncorking to honor `SEND_MORE`, with a 64 KiB threshold to avoid excessive corked data.
- `crypto_close` uses `gnutls_bye`, closes underlying sockets on full close, deinitializes the session, and clears `conn->crypto_session`.

Debug and inspection:
- `nbdkit_debug_tls_log` routes GnuTLS logs through nbdkit debug output.
- `nbdkit_debug_tls_session` enables negotiated-session summaries, auth type, peer certificates, group/curve/DH details, and kTLS status where supported.
- `nbdkit_peer_tls_dn` and `nbdkit_peer_tls_issuer_dn` return client certificate subject/issuer DN strings, or an allocated empty string when there is no applicable DN.
