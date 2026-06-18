# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/msg.c

SSH1 packet framing, encoding, decoding, CRC, and RSA padding utilities.

Key responsibilities:
- Allocates and sends SSH1 packets with padding, type byte, payload, and CRC32.
- Receives packets, decrypts, validates CRC, and skips DEBUG/IGNORE messages.
- Provides typed getters/setters for bytes, shorts, longs, strings, byte arrays, mpints, and RSA public keys.
- Implements SSH1-style RSA PKCS#1-like padding/unpadding helpers.

Important functions:
- `allocmsg`, `sendmsg`, `recvmsg`.
- `getstring`, `putstring`, `getmpint`, `putmpint`, `getRSApub`, `putRSApub`.
- `sum32`/`initsum32`: CRC table and calculation.
- `rsapad`, `rsaunpad`, `mptoberjust`, `rsaencryptbuf`.

Risks/quirks:
- Packet size hard limit is 256 KiB.
- Uses CRC32, not a MAC, reflecting SSH1 design.
- `rsaunpad` calls `error` on malformed padding.
