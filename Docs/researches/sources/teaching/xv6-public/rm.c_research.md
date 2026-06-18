# File Research: sources/teaching/xv6-public/rm.c

User-space remove utility.

Behavior:
- Requires at least one path.
- Calls `unlink` for each argument.
- Stops after first failed deletion and prints a diagnostic.
