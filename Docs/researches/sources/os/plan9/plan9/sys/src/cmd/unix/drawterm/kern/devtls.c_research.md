# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtls.c

Implements Plan 9 TLS device `#a/tls`, a TLS 1.0 / SSL 3.0 record-layer engine over an existing channel.

Key behavior:
- Exposes `tls`, `clone`, `encalgs`, `hashalgs`, and per-connection `ctl`, `data`, `hand`, `status`, and `stats`.
- Separates handshake traffic (`hand`) from application data (`data`).
- Supports state transitions for closed, handshaking, open, remote/local close, alerting, and errored states.
- Reads TLS records from the wrapped channel, validates version and length, decrypts, checks MAC, handles alerts, queues handshake records, and exposes application records.
- Writes handshake/application records with headers, MAC, optional encryption, and change-cipher handling.
- Supports SSL2-format initial ClientHello compatibility for handshakers.
- `ctl` supports `fd`, `version`, `secret`, `changecipher`, `opened`, `alert`, and `debug`.
- Tracks byte counters for data and handshake input/output.

Algorithms:
- Hashes: clear, MD5, SHA1.
- Encryption: clear, RC4-128, 3DES-EDE-CBC.
- Uses SSL3-specific MAC packing for SSL3 and HMAC-style packing for TLS1.0.

Important interfaces:
- Handshake policy and certificate logic are outside this file; this is the record layer.
- `tlsdevtab` registers device character `a`.

Notable risks:
- Maximum TLS devices grow from 128 to 1024.
- Only old SSL3/TLS1.0-era algorithms are implemented.
- Error handling sends TLS alerts and wakes the handshake queue with textual errors.
