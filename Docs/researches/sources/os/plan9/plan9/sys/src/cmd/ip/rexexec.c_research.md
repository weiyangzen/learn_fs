# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rexexec.c

Authenticated remote command executor intended to be run by `listen`.

Key behavior:
- Authenticates on stdin/stdout using `auth_proxy()` with `proto=p9any role=server`.
- Rejects authenticated user `none`.
- Changes uid/name space with `auth_chuid()`.
- Reads a NUL-terminated command from stdin into an 8192-byte buffer.
- Sets `service=rx` and execs `/bin/rc -lc <command>`.

Integration:
- Relies on Plan 9 auth server and listen-service fd wiring.

Risks and notes:
- Remote command execution is intentional but high privilege; security rests on auth_proxy/auth_chuid.
- Full buffer without NUL forces final byte to NUL.
