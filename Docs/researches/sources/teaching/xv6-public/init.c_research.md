# File Research: sources/teaching/xv6-public/init.c

Initial user-space process.

Behavior:
- Opens or creates `console`, then duplicates fd 0 to stdout and stderr.
- Repeatedly forks and execs `sh`.
- Waits for the shell process; reports and reaps unrelated orphaned children as `zombie!`.
- Exits only on fatal fork/exec paths.

Role:
- First long-lived user process after `initcode.S` execs `/init`.
