# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devtls.c

## Role

Implements Plan 9 `#a/tls`, a kernel TLS 1.0 / SSL 3.0 record-layer device layered over an existing open channel. User-space handshake code drives protocol setup through control commands, while this device encrypts/decrypts records.

## Main Data

`TlsRec` stores the underlying channel, state, negotiated version, byte counters, inbound/outbound `OneWay` cipher state, pending application data, raw unprocessed bytes, handshake queue, ownership, and permissions. `Secret` describes one cipher/MAC direction. Supported record types, alerts, and state bits are local enums. The device keeps a growable table of up to 1024 conversations.

Supported algorithms are `clear`, `rc4_128`, `3des_ede_cbc` and MACs `clear`, `md5`, `sha1`, with SSL3 custom MAC or TLS HMAC depending on version.

## Control Flow

`clone` creates a conversation. `ctl` commands bind an fd and version, set exact protocol version, install pending secrets, send ChangeCipherSpec, mark application data opened, and send alerts. `hand` exposes handshake records via a queue; `data` exposes application records; `status` and `stats` report state and counters.

Inbound `tlsrecread` reads record headers and bodies without losing sync on interrupt, accepts initial SSL2-format ClientHello, validates version and length, decrypts, checks MAC, applies cipher change, queues handshake records, handles alerts, or stores application data. Outbound `tlsrecwrite` fragments to `MaxRecLen`, prepends headers, computes MAC, encrypts, and writes blocks to the underlying channel.

## Dependencies

Depends on Plan 9 device, queue, block, fd/channel APIs and `<libsec.h>` RC4, DES3, MD5, SHA1, HMAC helpers.

## Risks

Only legacy SSL3/TLS1.0-era algorithms are supported. CBC padding/MAC handling is hand-coded and comments acknowledge timing-attack concerns. State transitions rely on user-space handshake correctness. `tlshangup` frees only the head of `unprocessed` with `freeb`, not `freeblist`, if it can be a chain.
