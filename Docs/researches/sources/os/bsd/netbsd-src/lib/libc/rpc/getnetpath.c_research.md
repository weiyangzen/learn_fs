# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetpath.c

Read completely: 286 lines.

Implements `setnetpath()`, `getnetpath()`, `endnetpath()`, and the shared `_get_next_token()` helper for RPC NETPATH iteration. If `NETPATH` is unset, a netpath session falls back to `setnetconfig()`/`getnetconfig()` and returns only `NC_VISIBLE` transports. If `NETPATH` is set, it copies the environment string, splits it on `:`, and resolves each netid with `getnetconfigent()`.

The session tracks netconfig entries allocated by `getnetconfigent()` so `endnetpath()` can free them. Invalid netids are silently skipped, matching the historical API behavior. `_get_next_token()` mutates the input string, supports escaped separators and backslashes, and is also used by `getnetconfig.c` for comma-separated lookup lists.

Reliability notes: `_get_next_token()` uses overlapping `strcpy()` for in-place compaction, which the source itself marks with `XXX`. The `ncp_list` append path stores only a head pointer and assigns `head->next` for later entries, so more than two returned NETPATH entries can overwrite the earlier second link and leak/lose cleanup tracking.
