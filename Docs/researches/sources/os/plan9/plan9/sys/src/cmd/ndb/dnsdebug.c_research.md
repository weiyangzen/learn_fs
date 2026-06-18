# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsdebug.c

Interactive/batch DNS resolver debugger built on the same resolver/cache code as `dns`. It can query default configured DNS servers or an explicit `@server`, optionally with resolver mode and external `/net.alt` mode.

It initializes DNS structures, installs a pretty `%R` formatter, opens the database, and either executes command-line queries or runs an interactive prompt. Each prompt flushes cache with `dnpurge()` before querying.

`doquery()` chooses default `ip` vs `ptr`, handles trailing-root dots, synthesizes IPv4 `in-addr.arpa` names for PTR queries, creates a `Request`, and calls `dnresolve()`. Output prints separator lines and formatted answers.

Explicit server support is implemented by `setserver()`, `squirrelserveraddrs()`, `preloadserveraddrs()`, and `getdnsservers()`: server hostnames are resolved first with resolver mode temporarily disabled, then preloaded into cache for subsequent resolver-mode queries.

This tool reuses production resolver paths but replaces logging with human-readable print output. Risks are debugger-specific: IPv6 reverse synthesis is marked TODO, and temporary server state is global.
