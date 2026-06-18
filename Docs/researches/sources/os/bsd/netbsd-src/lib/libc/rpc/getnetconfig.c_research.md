# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetconfig.c

Read completely: 691 lines.

Implements the `/etc/netconfig` access API: `setnetconfig()`, `getnetconfig()`, `endnetconfig()`, `getnetconfigent()`, `freenetconfigent()`, `nc_sperror()`, and `nc_perror()`. It keeps a global parsed-entry cache (`netconfig_info`) shared by active sessions, with per-session cursors and a reference count so repeated scans can reuse parsed `struct netconfig` records.

Parsing is done in-place on a line buffer: `parse_ncp()` tokenizes netid, semantics, flags, protocol family, protocol, device, and comma-separated lookup libraries. The resulting `struct netconfig` string pointers mostly point into the stored line buffer, while `nc_lookups` is separately allocated as an array of pointers into that same buffer. `getnetconfigent()` either duplicates cached entries via `dup_ncp()` or opens and scans `NETCONFIG` independently.

Thread support is partial: only `nc_error` is made thread-specific under `_REENTRANT`; the global file handle and parsed-entry cache are not protected here. Reliability notes: malformed records set `NC_BADFILE`; missing database sets `NC_NONETCONFIG`; many allocation failures just return `NULL`. Lookup-list `realloc()` is not checked before assignment in `parse_ncp()`, so allocation failure there can lose the original pointer.
