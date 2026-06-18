# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/util.c

Utility functions for `htmlfmt`.

- Provides checked allocation helpers `emalloc`, `erealloc`, `estrdup`, `estrstrdup`, `eappend`, and `egrow`.
- Provides `growbytes()` for append-only byte buffer growth with null termination.
- Provides `error()` that prints a formatted message to fd 2 and exits.

Notable concern: `error()` prefixes messages with `Mail: `, likely copied from another program and misleading for `htmlfmt`.
