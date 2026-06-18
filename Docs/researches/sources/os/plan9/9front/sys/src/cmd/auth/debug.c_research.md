# File Research: sources/os/plan9/9front/sys/src/cmd/auth/debug.c

Diagnostic tool for Plan 9 authentication setup and factotum keys.

Key responsibilities:
- Scans `/mnt/factotum/ctl` for `p9sk1` and `dp9ik` keys.
- Locates/dials auth servers for a key's auth domain, printing the lookup path.
- Prompts for a password and tests whether ticket requests decrypt correctly.
- Supports the `dp9ik` PAK preliminary exchange before ticket tests.
- Verifies returned client/server tickets and challenge echo values.

Dependencies:
- Uses factotum control format, Plan 9 auth server ticket routines, `csgetvalue`, `dial`, ndb/cs lookup, PAK helpers, and authsrv ticket conversion.

Research notes:
- This is a troubleshooting command, not a service.
- It performs interactive password prompting and clears password buffers after use.
