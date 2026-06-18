# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.c

Plan 9 telnet client.

Key behavior:
- Dials target TCP telnet service and optionally posts a pipe in `/srv`.
- Uses shared memory for communication flags between keyboard and network processes.
- `fromkbd()` reads local input, supports control menu on Ctrl-\ when not in binary mode, converts newline to CR/LF according to option state, and writes to network.
- `fromnet()` reads network data, handles TELNET IAC control sequences via `telnet.h`, normalizes CR/LF output when requested, and writes to screen.
- Menu supports break, interrupt, quit, return-mode toggle, option probes, shell escape, and continue.
- Sends terminal type and X display location through subnegotiation handlers.

Integration:
- Shares option negotiation implementation in `telnet.h`.
- Uses `/dev/consctl` raw mode to control local terminal behavior.

Risks and notes:
- `xlocsub()` uses `strncpy(p, term, p - buf - 2)`, a negative/incorrect bound expression, likely a bug.
- Uses two cooperating processes and notes to terminate peers.
