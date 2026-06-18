# File Research: sources/os/plan9/9front/sys/src/cmd/rx.c

`rx.c` runs a command on a remote host, trying multiple remote execution protocols. It builds a shell command string from argv, dials the target service, authenticates where needed, relays stdin to the remote side in a child, and copies remote output to stdout.

Connection order is Plan 9 `rcpu`, Plan 9 `rexexec`, SSH if an SSH port is reachable, then TCP `shell`. `call` builds network addresses with `netmkaddr` and `dial`.

`rcpu` authenticates with `auth_proxy` using p9any, wraps the connection in TLS with a PSK derived from the auth secret, sends an `rx` service request, then relays data. `rex` also uses p9any auth, then writes the command as a NUL-terminated string.

`tcpexec` implements old BSD-style shell authentication by sending local user, remote user, and command strings, then reading an authentication status byte and streaming output. It optionally converts or strips carriage returns.

`sshexec` execs `/bin/ssh`, preserving `-r` and remote user options when applicable. `send` forks a stdin-forwarder and optionally writes a zero-length EOF marker when stdin closes.

Options control EOF behavior (`-e`), carriage-return handling (`-T`, `-r`), auth key pattern (`-k`), and remote user (`-l`).
