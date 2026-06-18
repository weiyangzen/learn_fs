# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshserve.c

SSH1 server command.

Key responsibilities:
- Parses server cipher/auth options and client address.
- Generates ephemeral server RSA key.
- Performs SSH1 server handshake and authentication.
- Accepts pty/options/exec-shell/exec-command messages.
- Starts local shell command or telnetd session and bridges stdio over SSH packets.
- Sends exit status or disconnect.

Important functions:
- `main`: setup and handshake.
- `fromnet`: pre-exec option handling, then stdin channel loop.
- `startcmd`: forks command environment and starts stdout/stderr copyout processes.
- `copyout`: sends local fd output as SSH stdout/stderr data.

Notable behavior:
- Shell mode runs `/bin/ip/telnetd -tn`; command mode runs `/bin/rc -lc cmd`.
- Sets `user`, `sysname`, `tz`, and `service` environment variables for child.

Risks/quirks:
- Default server auth list is `tis`.
- Ephemeral RSA key is generated with 768 bits.
- Some unsupported client messages receive generic failure.
