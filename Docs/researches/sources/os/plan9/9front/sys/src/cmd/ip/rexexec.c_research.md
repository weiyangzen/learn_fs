# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rexexec.c

This is a remote execution service wrapper intended to be invoked by `listen`. It authenticates the peer with Plan 9 auth protocol `p9any` in server role.

After authentication, it rejects user `none`, changes uid with `auth_chuid`, and updates the network connection’s owner/mode to the authenticated cuid. It then reads a NUL-terminated command from fd 0 into an 8 KiB buffer.

Finally it sets environment variable `service=rx` and execs `/bin/rc -lc <command>`. It is small but security-sensitive: the effective user is established by Plan 9 auth before command execution.
