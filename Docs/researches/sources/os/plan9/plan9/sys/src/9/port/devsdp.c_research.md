# File Research: sources/os/plan9/plan9/sys/src/9/port/devsdp.c

Purpose: Secure Datagram Protocol device `#E`, providing encrypted/authenticated/compressed datagram conversations over an underlying packet channel. It exposes clone, per-conversation control/data/control-channel files, status, stats, remote stats, and log files.

Key structures:
- `Sdp`: per-attached filesystem state with conversation table and log.
- `Conv`: conversation state machine, owner/permissions, underlying channel, local/remote stats, retry timers, algorithms, and one-way input/output state.
- `OneWay`: sequence/window state, control-message state, cipher/auth/compression state.
- `Algorithm`, `CipherRc4`, and `AckPkt` implement selectable transforms and stats acknowledgements.

Key logic:
- `sdpclone` allocates/reuses a conversation and initializes permissions and sequence window.
- Control writes configure `dial`, `accept`, simulated `drop`, `cipher`, `auth`, `comp`, `insecret`, and `outsecret`.
- Connection state machine handles open request/ack/ack-ack, close/close-ack, reset, retries, keepalives, and timeout closure.
- Data packets carry type/subtype and 24-bit sequence numbers with wrap tracking, duplicate/reorder detection, optional auth, optional cipher, and optional thwack compression.
- Reliable control channel keeps one outstanding control packet, retransmits until acknowledged, and propagates stats in control ACKs.
- Background `sdpackproc` scans conversations once per second for retry/keepalive work.
- `convreader` drains the underlying channel when no data file is open so control traffic can still progress.

Dependencies and integration:
- Uses Plan 9 `netif.h`, `Log`, `Block`, `Queue`-like block I/O, `libsec` MD5/SHA1/DES/RC4, and `thwack` compression.

Risks and notes:
- Algorithms are old: DES, RC4, MD5 HMAC, SHA1 HMAC.
- State transitions are lock-sensitive and use background reader processes plus timer scanning.
- Sequence window is 32 packets; older packets are rejected and duplicates counted.
- The file is protocol implementation rather than a general filesystem component, despite living under `port`.
