# File Research: sources/virtualization/nbd/crypto-gnutls.c

GnuTLS-backed TLS session and proxy implementation.

It defines `tlssession`, initializes certificate credentials, optional trust anchors, optional client/server certificate/key files, hostname verification callback, GnuTLS session priority, and server certificate request behavior. The default priority string allows TLS 1.2.

`tlssession_mainloop()` performs a TLS handshake on the encrypted FD, switches encrypted and plaintext FDs to nonblocking mode, then runs a `select()` loop moving data between plaintext and encrypted endpoints. It uses two circular buffers: plaintext-to-crypt and crypt-to-plaintext. It handles pending GnuTLS records, EOF propagation, interrupted sends, `GNUTLS_E_AGAIN`, shutdown, and buffer cleanup.

The code also has custom GnuTLS push/pull functions activated when `SOCKET_WRAPPER_DIR` is set, improving compatibility with socket-wrapper based tests.

Certificate verification checks trust status, revocation/expiration/activation, X.509 type, peer cert import, and optional hostname matching.
