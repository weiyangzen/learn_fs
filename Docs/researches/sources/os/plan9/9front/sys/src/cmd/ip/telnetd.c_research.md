# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnetd.c

This is the Plan 9 telnet daemon. It authenticates users, creates a shell namespace, simulates `/dev/cons` and `/dev/consctl`, and bridges telnet network input/output to an interactive rc shell.

Key behavior:
- Supports raw/no-protocol modes, trusted user mode, explicit user, no-`none` controls, and noworld-only login.
- Uses p9cr challenge-response auth or password login for noworld accounts.
- Negotiates echo, terminal type, and X display options unless protocol mode is disabled.
- Implements cooked-line editing, echo, CR/LF normalization, EOF, word erase, line kill, and interrupt notes.
- Creates pipe-backed `/dev/cons` and `/dev/consctl`, sharing console raw/hold state via a shared segment.

Research notes:
- Includes `../ip/telnet.h`, which defines global option state and negotiation functions.
- Logs auth/session events through `syslog` under `telnet`.
