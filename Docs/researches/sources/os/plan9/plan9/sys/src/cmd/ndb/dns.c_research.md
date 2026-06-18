# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.c

Main 9P DNS service mounted as `/net/dns` and optional UDP DNS server supervisor. It parses daemon flags, initializes cache/database state, publishes `/srv/dns...`, restarts child DNS service processes, and handles local 9P file requests.

Global configuration (`Cfg cfg`) is set from options: serving UDP (`-s`), resolver/forward-only mode (`-r`/`-F`), no recursion (`-R`), straddling inside/outside networks (`-o`), debug/testing, cache target, forwarding targets, NDB file, alternate net mount, and zone refresh program.

The 9P file contains one synthetic file `dns`. Writes accept commands (`age`, `debug`, `dump`, `poolcheck`, `refresh`, `restart`, `stats`, `target`) or DNS queries of the form `domain type`. Replies are buffered in `Mfile.reply` with offsets per RR so reads return one RR at a time.

`io()` dispatches 9P requests under request activity tracking and supports slave process escape through `setjmp`. Query writes call `dnresolve()` and `respond()` formats answers as `%R` or `%Q` when request name is prefixed by `!`.

Process model is explicit: a restarter creates `/srv/dns`, then repeatedly forks a child with separate namespace; the child may start UDP and notify processes and serves 9P until restart. This avoids deadlock from serving its own namespace.

Risks include complex restart/remount behavior, shared global cache across forked processes, fixed reply limits (`Maxreply`, `Maxrrr`), and management commands exposed through the writable 9P file.
