# File Research: sources/os/plan9/plan9/sys/src/9/boot/boot.c

Main Plan 9 boot program logic.

Key behavior:
- Reopens console fds, binds environment and service namespaces, parses `-k`, `-m`, and `-f` options.
- Handles debug flags from environment (`debugboot`, `nousbboot`).
- Starts USB boot support before auth so USB nvram/parts can be visible.
- Selects boot method through `rootserver()` using `nobootprompt`, `bootargs`, argv, or interactive prompt.
- Loads keyboard map if configured.
- Binds device namespaces for nvram/disk discovery and reads partition tables if requested.
- Starts authentication/factotum, refreshes namespace, restarts USB partfs under new hostowner, connects to root server, negotiates 9P, posts `/srv/boot`, mounts root, sets time, starts swap kproc, and execs init.
- Supports optional old 9P compatibility through `/srvold9p`.

This is the high-level boot transition from kernel `initcode` environment to mounted root filesystem and `/arm/init` or configured init.
