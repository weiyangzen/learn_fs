# sources/user-network-fs/samba/source3/utils/net_help.c

Purpose: implements generic `net help` behavior using the top-level command table stored in `c->private_data`.

Important APIs/types/functions: public `net_help()` plus internal `net_usage()` and `net_help_usage()`.

Control flow: no args print command summaries. `help` sets full usage mode and prints all usage. Any other argument sets full usage mode and calls `net_run_function()` so the named command prints detailed usage. `net_usage()` iterates a NULL-terminated `struct functable`.

State and persistence: no persistence; mutates `c->display_usage` for the current help path and reads `c->private_data`.

Dependencies/integration: depends on the global dispatcher putting a valid functable in `net_context.private_data`; uses `net_common_flags_usage()`.

Risks: invalid `private_data` would crash or print garbage. Usage return codes may be failure-like because `net_usage()` returns `-1`.

Test signals: `net help`, `net help help`, `net help <command>`, invalid command, malformed private data in unit tests, translated usage.
