## sources/user-network-fs/libtirpc/src/getnetconfig.c

Purpose: Implements `/etc/netconfig` access APIs: `setnetconfig`, `getnetconfig`, `endnetconfig`, `getnetconfigent`, `freenetconfigent`, `nc_sperror`, and `nc_perror`.

Important APIs and control flow: A global `netconfig_info` cache stores parsed entries and a shared file pointer protected by `nc_db_lock`. `setnetconfig` opens `NETCONFIG`, increments a reference count, and returns a session handle. `getnetconfig` returns cached entries or reads/skips comments, allocates a list node and `struct netconfig`, then parses fields with `parse_ncp`. `endnetconfig` decrements references and frees the cache/file when the final handle closes. `getnetconfigent` searches the cache or scans the file for one netid and returns a duplicated independent entry.

State and persistence: Persistent process cache mirrors `/etc/netconfig` until all sessions end. Error state is thread-specific via `nc_key`, with static fallback.

Dependencies and integration: Netconfig drives transport selection in client creation, broadcasts, key/crypt clients, and netpath.

Risks and test signals: Parser mutates line buffers and has complex ownership rules. Tests should cover malformed lines, lookup-list parsing, multiple nested sessions, thread-specific errors, `getnetconfigent` duplication/freeing, and cache teardown.
