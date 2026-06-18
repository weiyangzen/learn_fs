# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcent.c

Read completely: 224 lines.

Implements the legacy `/etc/rpc` database API: `setrpcent()`, `getrpcent()`, `endrpcent()`, `getrpcbyname()`, and `getrpcbynumber()`. A single static `rpcdata` object holds the open file, stay-open flag, current `struct rpcent`, alias pointer array, and line buffer.

`interpret()` copies the input line into the shared buffer, skips comments and malformed lines by recursively calling `getrpcent()`, parses the service name, numeric RPC program number via `atoi()`, and up to 34 aliases. `getrpcbyname()` checks both canonical names and aliases; `getrpcbynumber()` scans sequentially.

This is process-global and not thread-specific. Returned `struct rpcent` data points into static storage overwritten by the next lookup. Parsing is permissive and historical: bad/comment lines are skipped rather than surfaced as explicit errors.
