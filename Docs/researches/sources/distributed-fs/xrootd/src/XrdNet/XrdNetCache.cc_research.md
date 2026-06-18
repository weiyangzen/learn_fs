## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.cc

Purpose: Implements a mutex-protected address-to-hostname DNS cache for `XrdNetAddrInfo`.

Important APIs and functions: Constructor, `Add`, `Find`, private `Expand`, `GenKey`, and `Locate` are implemented. Static `keepTime` controls entry expiry.

Control flow: `Add` generates an address key, locks, updates an existing entry or expands the hash table when the load threshold is crossed, then prepends a new entry. `Find` generates the key, locks, locates the item, returns a duplicated hostname if unexpired, or unlinks and deletes expired entries. `Expand` grows table size using a Fibonacci step and rehashes entries.

State and persistence: Process-local heap hash table, item chains, expiration times, and static keep time. The destructor intentionally does not clean the table because the cache is designed as a never-deleted singleton-style object.

Dependencies and integration points: Uses `XrdNetAddrInfo` for socket address access and `XrdSysMutex` for locking. `XrdNetAddr::SetCache` installs this cache for reverse lookups.

Risks: Constructor does not check `malloc` before `memset`. `nashnum` is not decremented when expired items are removed, so load accounting can drift upward. `Find` returns `strdup` memory that callers must own and free. Static `keepTime` changes affect all cache instances.

Test signals: Add/find IPv4 and IPv6 names; reject Unix/invalid families; expire entries; update existing entries; force expansion; run concurrent add/find; validate caller frees returned names.
