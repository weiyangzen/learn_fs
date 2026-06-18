# File Research: sources/os/plan9/plan9/sys/src/cmd/netstat.c

Plan 9 network status utility. It lists active protocol conversations under `/net` or a supplied network root, optionally restricted to interfaces (`-i`), numeric output (`-n`), or selected protocols (`-p proto`).

For protocol stats, `nstat()` reads protocol directories and calls `pip()` on each conversation. `pip()` reads `status`, `local`, and `remote`, translates ports via `csgetvalue()` unless `-n`, and translates remote IPs to domain names through connection server lookup when possible.

`pipifc()` uses `readipifc()` to print interface device, MTU, IP, mask, network, and packet/error counters, dynamically sizing IP columns.

Risks include fixed buffers for status/local/remote paths and contents, assumptions about Plan 9 network file layout, and translation dependencies on `/net/cs` that can fail or block.
