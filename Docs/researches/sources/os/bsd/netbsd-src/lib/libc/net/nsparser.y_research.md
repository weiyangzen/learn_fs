# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nsparser.y

Yacc grammar for `nsswitch.conf`. It parses database entries of the form `database: source [criteria] ...`, constructs `ns_dbt` records, and stores them through `_nsdbtput()`.

Each source defaults to returning on `NS_SUCCESS`; criteria toggle return/continue bits for success, unavailable, not found, and try-again statuses. `_nsaddsrctomap()` rejects mixing `compat` with other sources, rejects duplicate sources, and logs source-addition failures.
