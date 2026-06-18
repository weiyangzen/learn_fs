# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnetd.c

Plan 9 telnet daemon and remote login shell launcher.

Key behavior:
- Parses flags to disable protocol, allow `none`, trust current user, set user, enable debug, or restrict to noworld accounts.
- Sends initial TELNET negotiation for echo, terminal type, and X display unless protocol is disabled.
- Authenticates through Plan 9 challenge/response or noworld password login; trusted mode uses current user.
- Creates shared console state and simulates `/dev/cons` plus `/dev/consctl` using pipes/binds.
- Forks an interactive `/bin/rc -il` in a separate process group with simulated console fds.
- Runs two data pumps:
  - `fromchild()` converts child output newline to CR/LF when not raw.
  - `fromnet()` handles TELNET protocol/control characters, local echo, cooked editing, EOF, and interrupt notes.
- Handles terminal type and X display subnegotiation by setting `TERM` and `DISPLAY`.

Integration:
- Invoked directly by listeners or via `rlogind`.
- Shares TELNET parser in `telnet.h`.
- Uses Plan 9 auth, namespace, and process-note mechanisms.

Risks and notes:
- `getremote()` closes fd even if `open()` failed.
- `termsub()` and `xlocsub()` use `strncpy()` without explicit NUL termination when `n == sizeof buffer`.
- Simulated console state depends on a shared segment and a helper process reading consctl commands.
