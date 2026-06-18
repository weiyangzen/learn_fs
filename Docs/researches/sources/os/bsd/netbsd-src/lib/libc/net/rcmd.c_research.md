# File Research: sources/os/bsd/netbsd-src/lib/libc/net/rcmd.c

Implementation of classic BSD remote-command and remote-user trust helpers. `rcmd()` / `rcmd_af()` resolve the target, canonicalize the host name when possible, and either use a local `RCMD_CMD`/rsh execution path for the shell service or the reserved-port network protocol through `resrcmd()`.

`resrcmd()` obtains reserved local ports, connects with retry/backoff on refusal, optionally creates the stderr side channel, validates the peer’s reserved stderr port, sends local user, remote user, and command strings, then waits for the server’s one-byte status. `rshrcmd()` instead forks, sets up socketpairs, drops to the local user, and execs either a local shell for same-user localhost or an rsh command with `-4`/`-6` as appropriate.

The file also implements `rresvport*()` reserved-port binding and `ruserok()` / `iruserok*()` trust checks. `.rhosts` handling temporarily switches effective uid/gid to the local user, requires regular owner-safe files, supports `+`, `-`, and netgroup syntax, and validates hostnames through forward/reverse address matching.
