# File Research: sources/os/plan9/9front/sys/src/9/port/devsdp.c

Purpose: Implements `#E`, the Secure Datagram Protocol device, providing encrypted/authenticated/compressed datagram conversations over an underlying packet channel.

Key logic:
- Exposes per-instance `sdp`, `clone`, `log`, and per-conversation `ctl`, `data`, `control`, `status`, `stats`, and `rstats`.
- `sdpclone` allocates/reuses conversations, initializes permissions, state, refs, and sequence window state.
- `ctl` commands configure `accept`, `dial`, packet drop simulation, cipher, auth, compression, and per-direction secrets.
- Connection state machine handles open request/ack/ack-ack, close/close-ack, reset, retry, timeout, and keepalive.
- Packet format includes type/subtype, 24-bit sequence numbers with wrap/window tracking, optional auth, optional cipher padding/IV, and optional thwack compression.
- Reliable control channel keeps one outstanding control packet, retransmits by timer, ACKs with local stats, and refreshes remote stats.
- Data path reads underlying blocks, filters control traffic, returns data packets, and starts a background reader when the data file is closed.
- Algorithms include null/DES/RC4 ciphers, null/MD5/SHA1 auth declarations, implemented MD5 HMAC auth, and thwack compression.

Dependencies and integration:
- Uses `netif.h`, `Log`, `Block` I/O, `libsec` DES/RC4/MD5/SHA1 primitives, and `thwack` compression.

Risks and notes:
- Cryptographic algorithms are legacy: DES, RC4, MD5-HMAC, and SHA1-era naming.
- Sequence window is 32 packets; duplicates, reorders, missing packets, bad auth, and bad compression are counted.
- `shaauthinit` only clears auth state in this file; SHA auth is listed but not implemented here.
