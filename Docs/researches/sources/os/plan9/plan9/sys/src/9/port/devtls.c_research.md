# File Research: sources/os/plan9/plan9/sys/src/9/port/devtls.c

Purpose: TLS 1.0 / SSL 3.0 record-layer device `#a/tls`. It wraps an existing fd and exposes record-protected `data`, handshake `hand`, `ctl`, `status`, `stats`, and algorithm-list files.

Key structures:
- `TlsRec`: per-record-layer connection, state, protocol version, underlying channel, statistics, handshake queue, processed/unprocessed input, in/out secrets, owner, permissions.
- `OneWay`: input/output I/O lock, secret lock, sequence number, current secret, and pending secret.
- `Secret`: cipher/MAC algorithm names, encrypt/decrypt callbacks, unpadding callback, MAC callback, block size, MAC key, and cipher key.
- `TlsErrs`: maps internal alert IDs to SSL3/TLS alert codes and user-facing messages.

Key logic:
- `clone` creates a TLS record object; opening `hand` allocates a handshake queue.
- `ctl` commands configure `fd`, negotiated `version`, pending `secret`, `changecipher`, `opened`, `alert`, and `debug`.
- `tlsrecread` parses records, including initial SSL2-format ClientHello compatibility, enforces version/length limits, decrypts, verifies MAC, handles change-cipher-spec, alerts, handshake queueing, and application data.
- `tlsrecwrite` frames handshake/application/alert/change-cipher records, computes MAC, encrypts, changes output cipher at the correct byte boundary, and writes to the underlying channel.
- `hand` reads deliver handshake messages and alert/error messages to user-level handshake code.
- Supports `clear`, `rc4_128`, `3des_ede_cbc`, `aes_128_cbc`, `aes_256_cbc`; MACs are `clear`, `md5`, and `sha1`.
- Provides SSL3 custom MAC packing and TLS HMAC packing.

Dependencies and integration:
- Uses Plan 9 block/channel I/O, `Queue`, `libsec` RC4/3DES/AES/MD5/SHA1/HMAC, and state transitions coordinated by locks and qlocks.

Risks and notes:
- Protocol support is capped at TLS 1.0/SSL3-era mechanisms.
- Record read has explicit interrupt-regurgitation handling to avoid losing consumed header bytes.
- CBC unpadding includes TLS strict pad validation; the comment acknowledges timing-sensitive MAC/pad errors.
- `status` and `stats` expose state, algorithm names, and byte counters.
