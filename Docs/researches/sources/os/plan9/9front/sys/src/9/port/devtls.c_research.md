# File Research: sources/os/plan9/9front/sys/src/9/port/devtls.c

Implements the Plan 9 TLS record-layer device, exposed as `#a/tls`. It supports SSL 3.0 through TLS 1.2 record framing, close/error alerts, application records, handshake record forwarding, and cipher-state changes controlled from user space.

The device presents `clone`, `encalgs`, `hashalgs`, and per-conversation files `ctl`, `data`, `hand`, `status`, and `stats`. A user-space handshaker opens `hand`, binds an underlying fd with `ctl fd`, sets protocol version and secrets, writes `changecipher`, and finally sends `opened` to permit application data on `data`.

Core state is held in `TlsRec`, with independent `OneWay` input/output cipher state, sequence counters, pending secrets, processed/unprocessed record blocks, and a handshake queue. `tlsrecread` parses and decrypts records, handles SSL2-format initial ClientHello compatibility, routes handshake/alert/application data, validates MACs or AEAD tags, and updates cipher state on ChangeCipherSpec. `tlsrecwrite` fragments output into records, computes AAD/MAC/tag, pads CBC records, encrypts, and writes to the underlying channel.

Supported algorithms include clear, RC4-128, 3DES-CBC, AES-CBC, ChaCha20-Poly1305 variants, AES-GCM variants, MD5, SHA1, and SHA256 HMAC. The code depends on Plan 9 block queues, device dispatch, `libsec`, and fd-to-channel kernel plumbing.

Security-sensitive points are the record error paths, CBC padding/MAC behavior, nonce handling for AEAD, and state transitions around `opened`, close notify, and fatal alerts.
