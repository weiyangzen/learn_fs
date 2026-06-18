# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/cron.c

Plan 9 cron daemon with per-user schedules and local/remote execution.

Key points:
- Maintains `/cron/lock` as an exclusive lock.
- Reloads `/cron/<user>/cron` files when qids change.
- Parses classic five-field cron time specs plus host and command.
- Rounds schedule processing to minutes and handles clock jumps.
- `rexec` forks jobs, switches user through kernel capabilities, and runs locally or over `rexexec` with `p9any` auth.
- `-c` creates the current user’s cron directory and file; `-d` prints parsed jobs.

Dependencies:
- Uses Plan 9 auth capability code duplicated from `as.c`, `auth_proxy`, and remote dial helpers.

Notable behavior:
- Commands are wrapped as `exec rc -c '...'` with quote escaping and redirected I/O.
