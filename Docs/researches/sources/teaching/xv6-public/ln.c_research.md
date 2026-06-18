# File Research: sources/teaching/xv6-public/ln.c

User-space hard-link utility.

Behavior:
- Requires exactly two arguments: old path and new path.
- Calls `link(old, new)`.
- Reports usage or link failure, then exits.
