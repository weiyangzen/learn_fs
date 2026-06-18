# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.c

This file implements the user-facing SSH client command, using `/net/ssh` for protocol work and copying bytes between terminal and channel data files.

Key behavior:
- Parses compatibility flags, user/remote syntax, netdir overrides, key selection, password/public-key disabling, raw/cooked behavior, and CR stripping.
- Ensures an SSH tunnel service is mounted by trying `/srv/netssh`, `/srv/ssh`, `/srv/ssh.$user`, or starting `/bin/netssh`.
- Forks a helper that speaks the `/net/ssh/keys` confirmation protocol through `/dev/cons`.
- Dials a connection under `/net/ssh`, authenticates via ctl messages, dials a session channel, writes a shell or exec request, and performs bidirectional data copying.
- Handles interactive escape command mode triggered by control-backslash at line start.

Important details:
- Authentication first tries public key (`ssh-userauth K`) unless disabled, then password (`ssh-userauth k`) via `auth_getuserpasswd`.
- Terminal raw mode is controlled through `/dev/consctl`.
- Shutdown writes `close` to the request file and sends `kill` to a note group fd.
- Remote command requests quote each argument into a single `exec` request.

Filesystem relevance:
- Direct: client of the `/net/ssh` filesystem plus `/srv`, `/dev/cons`, `/dev/consctl`, `/proc`, and environment files.
