# File Research: sources/os/plan9/9front/sys/src/cmd/ip/sol.c

This is an Intel AMT Serial-over-LAN and KVM redirection client.

Key behavior:
- Connects to AMT redirection ports 16995 with TLS or 16994 without TLS.
- Supports digest authentication through factotum and plaintext fallback.
- Provides raw console handling through `/dev/consctl`.
- For SOL, forks bidirectional forwarding between local console and AMT transmit/receive messages.
- For KVM mode, sends the KVM redirect command then relays bytes directly.

Research notes:
- Uses compact `send()`/`recv()` format strings for little-endian AMT records.
- On post-auth EOF, it kills the helper process and reconnects via `longjmp`.
