# File Research: sources/os/plan9/9front/sys/src/cmd/con/con.c

Implements `con`, an interactive terminal/network connection tool. It can connect to a device path, simple dialed byte stream, or BSD rlogin-style service, then shuttle bytes between local terminal and remote endpoint.

Options control baud, cooked/raw console mode, command execution over the connection, debugging, limited rlogin mode/user, keyboard suppression, carriage-return filtering/conversion, parity stripping, `/srv` posting, verbose dialing, and newline-to-carriage-return translation.

`simple`, `rlogin`, and `device` establish the three connection modes. `stdcon` forks two processes sharing memory: one handles keyboard-to-network (`fromkbd`), the other network-to-screen (`fromnet`).

Interactive control is entered with control-backslash (`0x1c`), offering break, quit, interrupt, return-filter toggle, continue, or local shell command execution. Raw mode is managed through `/dev/consctl`.

`system` runs `/bin/rc` with the network connection as stdout and a pipe for stdin, allowing local command output to be sent to the remote side.

Reliability behavior includes interrupt-tolerant `iread/iwrite`, first-error capture for dial fallback, notification handling for pipe/hangup/interrupt, and cleanup of posted `/srv` entries.
