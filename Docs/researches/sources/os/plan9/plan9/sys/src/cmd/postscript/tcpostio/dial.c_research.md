# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/dial.c

Purpose: Provides a non-Plan 9 `dial` compatibility routine for `tcpostio`, using BSD/POSIX sockets.

Key behavior:
- Parses `dest` in Plan 9-style `tcp!host!service` or `udp!host!service` format.
- Resolves host with `gethostbyname`.
- Resolves service by name or numeric string.
- Opens a socket or reserved local port if requested.
- Applies a 30-second `alarm` around `connect`.
- Attempts SO_KEEPALIVE handling on non-Plan 9 builds.
- Ignores Plan 9 `dir` and `cfdp` parameters.

Dependencies and integration:
- Used by `tcpostio.c` to connect to printer network services.
- Bridges Plan 9 code to traditional Unix networking.

Risks and notes:
- Several error paths leak `tdest`.
- `sp->s_port` is already network byte order on many systems; wrapping it in `htons` is suspicious.
- SO_KEEPALIVE setup appears to set the option to the existing false value rather than enabling it.
- Uses `gethostbyname`, `strtok`, and `alarm`, all legacy/global-state APIs.
