# File Research: sources/os/plan9/9front/sys/src/cmd/ssh.c

`ssh.c` is a compact SSH-2 client for 9front. It handles transport, key exchange, authentication, session/direct-tcp channels, terminal mode, and a raw mux mode used by companion tools.

Core protocol pieces:
- Defines SSH message numbers for transport, userauth, global requests, and channel operations.
- `vpack`/`vunpack`, `pack`, and `unpack` encode/decode SSH byte, uint32, string, raw buffer, and mpint fields.
- `sendpkt` and `recvpkt` implement packet framing, padding, sequence numbers, and optional `chacha20-poly1305@openssh.com` encryption/MAC after key exchange.
- `kex` performs Curve25519 key exchange, verifies RSA SHA-256 host signatures, checks host thumbprints, derives Chacha keys, and schedules rekeying.
- RSA helpers convert between Plan 9 `RSApub`/`mpint` and SSH wire formats.

Authentication:
- `noneauth`, `pubkeyauth`, `passauth`, and `kbintauth` try supported SSH userauth methods.
- Public-key auth uses factotum `/mnt/factotum/rpc`.
- Password auth uses `auth_getuserpasswd`; keyboard-interactive prompts on `/dev/cons`.

Channel handling:
- `dispatch` handles global messages, disconnect/debug/banner, rekey, channel data, extended data, flow-control window adjustments, EOF/close, and exit status/signal.
- Main opens either a session channel or `direct-tcpip` channel via `-W`.
- Supports pty/shell, exec, subsystem command beginning with `#`, raw terminal mode, window-change notes, and `-X` mux passthrough.

Important risks:
- This client intentionally supports a narrow algorithm set: Curve25519, RSA SHA-256 host key/signature, Chacha20-Poly1305, no compression.
- Several fatal paths abort the process on malformed protocol input.
- A likely typo sets `recv.chan = send.win = 0` where `send.chan` was probably intended, though later channel confirmation overwrites channel ids for normal operation.
