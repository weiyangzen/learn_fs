# File Research: sources/teaching/xv6-public/kill.c

User-space `kill` utility.

Behavior:
- Requires at least one PID argument.
- Converts each argument with `atoi` and invokes the `kill` system call.
- Prints usage on missing arguments.

It does not report per-PID kill failures.
