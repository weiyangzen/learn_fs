# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rlogind.c

Compatibility wrapper for rlogin-style service startup.

Key behavior:
- Reads four NUL-terminated strings from stdin: initial error/status, remote user, local user, and terminal.
- Acknowledges by writing one NUL byte.
- Defaults empty local user to remote user.
- Logs target user and execs `/bin/ip/telnetd -n -u <user>`.

Integration:
- Delegates actual terminal/session handling to `telnetd`.
- `-n` disables telnet protocol handling in telnetd.

Risks and notes:
- Trusts incoming rlogin identity enough to pass `-u`; telnetd authentication/trust flags determine security.
