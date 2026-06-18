# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsdebug.c

Interactive and one-shot DNS debugging client using the same resolver core.

Key elements:
- Supports flags for cached database mode, resolver mode, debug logging, alternate database/net mount, and database file selection.
- Initializes DNS core, opens database, loads DB into cache, and accepts either command-line or interactive queries.
- Provides pretty RR formatter `%P` that aligns owner, TTL, type, and data.
- Implements verbose `logreply` and `logrequest` hooks for resolver network tracing.
- `getdnsservers` can override configured resolvers with an `@server` or `!server` temporary server, where `!` selects DoT-style override naming.
- `doquery` defaults to A lookups for names and PTR lookups for numeric IPs, converts PTR names with `mkptrname`, and calls `dnresolve`.
- `docmd` supports `refresh` and temporary server queries.

Notable behavior:
- Unless `-c` is set, the cache is purged before each query.
- Temporary server overrides are cleared after the query.
- Literal IP server overrides create synthetic address RRs and attach them authoritatively.

Risks and quirks:
- Mutates the query string in place when stripping a trailing dot.
- Depends on shared DNS globals and packet conversion code, but runs as a standalone command.
