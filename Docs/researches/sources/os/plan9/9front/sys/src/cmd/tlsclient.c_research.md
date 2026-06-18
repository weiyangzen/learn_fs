# File Research: sources/os/plan9/9front/sys/src/cmd/tlsclient.c

Read completely: 174 lines, 3108 bytes.

Standalone TLS client wrapper. It opens a dial string or existing file, optionally performs Plan 9 auth, starts a TLS client session, verifies a server certificate against thumbprints, optionally dumps the server certificate, then either execs a command over the TLS fd or shuttles stdin/stdout.

Key behavior:
- Flags cover debug trace, auth key spec, thumbprint allow/exclude files, client certificate, server-name/SNI, certificate dump path, and `-o` for opening a file instead of dialing.
- Uses `tlsClient`, `initThumbprints`, `okCertificate`, `readcert`, and `auth_proxy`.
- For no command, forks one transfer direction and copies the other in the parent.

Security/reliability notes:
- Without `-t`, certificate thumbprint verification is not performed here.
- Auth mode uses `p9secret` PSK material from `auth_proxy`.
- The child shutdown note string is fixed and non-semantic.
