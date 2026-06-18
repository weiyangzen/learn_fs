# File Research: sources/virtualization/libnbd/lib/crypto.c

Implements TLS configuration and the GnuTLS-backed socket wrapper used after `NBD_OPT_STARTTLS`.

Key public configuration:
- `nbd_unlocked_set_tls`, `get_tls`, `get_tls_negotiated`
- Certificate directory, peer verification, username, hostname, PSK file, and priority setters/getters.
- Username fallback uses `$LOGNAME`, then `getlogin_r`.

TLS socket ops:
- `tls_recv`, `tls_send`, `tls_pending`, `tls_get_fd`, `tls_shut_writes`, `tls_close`.
- Converts GnuTLS retry conditions to `EAGAIN`.
- Downgrades qemu-nbd-style unclean TLS close after client write shutdown to EOF/debug.

Credential setup:
- PSK mode reads `username:hexkey` entries from the configured PSK file and extends the priority string with PSK key exchanges.
- Certificate mode searches explicit cert dir, user pki dirs, or system config pki dir, loading CA, optional CRL, client cert/key, and numbered extra client cert/key pairs.
- Falls back to system CA when no private cert dir is found.
- Peer verification uses configured TLS hostname, falling back to connection hostname.

State-machine integration:
- `nbd_internal_crypto_create_session`: initializes nonblocking GnuTLS session, sets SNI, credentials, transport fd, timeout, and returns a TLS socket wrapper.
- `nbd_internal_crypto_is_reading`: reports GnuTLS handshake direction.
- `nbd_internal_crypto_handshake`: advances handshake and distinguishes complete, retry, and fatal error.
- `nbd_internal_crypto_debug_tls_enabled`: logs negotiated cipher, key exchange, MAC, and optional kTLS status.

Compile-time behavior:
- Without GnuTLS, TLS setters only allow disabling TLS, public support checks report false elsewhere, and internal TLS functions abort if reached.

Research notes:
- TLS is layered as a socket ops wrapper, so most library I/O is transport-agnostic.
- Certificate search behavior is security-sensitive because URI local-file parameters are separately policy-gated in `uri.c`.
