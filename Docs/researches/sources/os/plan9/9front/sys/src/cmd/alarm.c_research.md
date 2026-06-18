# File Research: sources/os/plan9/9front/sys/src/cmd/alarm.c

Small command wrapper that runs another command and delivers an alarm note after a timeout.

Important behavior:
- Usage is `alarm time command [arg ...]`.
- Parses seconds with optional millisecond fraction and calls `alarm(t)` in milliseconds.
- Forks the target command in a new process sharing memory/render state as configured by `rfork`.
- The note handler reposts received notes to the process group, then uses default note handling.
- If direct `exec` fails, it retries under `/bin`.

The program is Plan 9 specific because it relies on notes, `rfork`, `postnote`, and `wait`.
