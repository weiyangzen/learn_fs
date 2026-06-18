# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/chat.c

This file provides debug logging, syslog logging, panic handling, and a `/srv` control endpoint for runtime chat/debug verbosity.

Key routines:
- `chatsrv` creates a `/srv` file exposing a pipe; writes to it adjust `chatty`, `rpcdebug`, and `conftime`.
- `killchat` removes the service file and kills the helper process at exit.
- `chat` prints debug messages to fd 2 when `chatty` is enabled.
- `clog` logs to stderr or Plan 9 syslog depending on verbosity.
- `panic` logs a fatal error and exits.

Important interactions:
- Shared by all `9nfs` server programs.
- Updates global `rpcdebug` used by RPC serialization/debug code.
- `conftime` forces config reload timing when chat control receives commands starting with `c`.

Research notes:
- `chatsrv` forks with `RFPROC|RFMEM`, sharing memory with the parent for debug-control variables.
