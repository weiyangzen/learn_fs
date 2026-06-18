# File Research: sources/os/plan9/plan9/sys/src/cmd/rx.c

Read status: complete, 266 lines.

`rx` runs a command on a remote host. It tries Plan 9 `rexexec` authentication using `p9any` and `p9sk2`, then SSH, then TCP shell service. It forwards stdin to the remote connection in a child process and writes remote output to stdout.

Options control EOF sending, CR-to-NL conversion, CR stripping, auth key pattern, and remote username. `tcpexec` implements BSD-style shell authentication, `rex` uses `auth_proxy`, and `sshexec` execs `/bin/ssh`.

Filesystem relevance: network/process utility rather than filesystem code, but it is used by `sam` remote startup paths and interacts with file descriptors/pipes.
