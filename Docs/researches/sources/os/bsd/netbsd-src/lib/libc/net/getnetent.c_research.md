# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnetent.c

Read completely: 166 lines.

This file implements sequential network database access: `setnetent`, `endnetent`, and `getnetent`.

It opens `_PATH_NETWORKS`, skips comments/malformed lines, parses network name, network number via `inet_network`, and up to 34 aliases into static storage. `setnetent`/`endnetent` also call host database open/close routines, preserving legacy resolver behavior.

Security/reliability notes: results use static globals and are not thread-safe. Alias count is capped by a fixed array; excess aliases are silently ignored.
