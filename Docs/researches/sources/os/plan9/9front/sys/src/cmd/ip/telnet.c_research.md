# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnet.c

This is the Plan 9 telnet client frontend. It handles dialing, terminal raw mode, keyboard/network forwarding, escape menu handling, and client-side telnet subnegotiation callbacks.

Key behavior:
- Options include debug, no-keyboard mode, CR handling, suppress local echo negotiation, and posting a pipe in `/srv`.
- Forks two processes: keyboard-to-network and network-to-screen.
- Recognizes Ctrl-\ escape menu for break, interrupt, quit, CR mode toggle, and shell command execution.
- Uses shared telnet negotiation code from `telnet.h`.
- Sends terminal type from `$TERM` and X display location from `$XDISP`.

Research notes:
- `xlocsub()` uses `strncpy(p, term, p - buf - 2)`, which appears to compute a negative/invalid remaining length; this is a likely bug.
