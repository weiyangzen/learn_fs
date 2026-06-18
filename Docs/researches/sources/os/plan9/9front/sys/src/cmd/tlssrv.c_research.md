# File Research: sources/os/plan9/9front/sys/src/cmd/tlssrv.c

Read completely: 147 lines, 2413 bytes.

Standalone TLS server wrapper. It accepts an already-open fd 0 connection, optionally authenticates the peer through Plan 9 auth, loads a certificate chain, starts `tlsServer`, then execs a command with stdin/stdout attached to the TLS connection.

Key behavior:
- Flags cover debug tracing, auth with or without `auth_chuid`, key spec, timeout, certificate file, syslog file, and remote system label.
- Requires either certificate material or PSK secret material.
- When full auth is selected, it changes user and attempts to chown the network connection to the authenticated user.

Dependencies:
- Uses `libsec`, `auth`, `readcertchain`, `tlsServer`, `auth_proxy`, `auth_chuid`, `syslog`, and Plan 9 fd operations.

Reliability notes:
- TLS failure exits success unless debug logs the failure, matching service-wrapper behavior but potentially hiding failed handshakes from callers.
