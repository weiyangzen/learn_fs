# sources/user-network-fs/nfs-utils/support/misc/tcpwrapper.c

Purpose: optional libwrap access-control support for RPC service requests, compiled only when `HAVE_LIBWRAP` is set. It translates caller socket addresses into printable addresses, consults tcp_wrappers through `hosts_access()`, and caches allow/deny decisions per caller/program.

Important APIs and types: `check_default(char *name, struct sockaddr *sap, unsigned long program)` is the exported decision point. Internal `haccess_t` entries are stored in a 1021-bucket `TAILQ` hash table keyed by printable address plus RPC program number. `present_address()`, `good_client()`, `check_files()`, `haccess_add()`, and `haccess_lookup()` support address presentation, libwrap lookup, hosts file change detection, and caching.

Control flow: `check_default()` formats the caller address, checks `/etc/hosts.allow` and `/etc/hosts.deny` mtimes, and returns a cached result if neither file changed. Otherwise local callers are allowed without consulting tcp_wrappers, nonlocal callers go through `request_init()`, `sock_methods()`, and `hosts_access()`, then the cache is updated and a debug log is emitted.

State and persistence: runtime state is the process-local static hash table plus static mtimes for the hosts files. The module reads persistent policy from `/etc/hosts.allow` and `/etc/hosts.deny` but never writes those files.

Dependencies and integration: depends on libwrap headers/functions, RPC sockaddr helpers (`nfs_sockaddr_length()`, `nfs_compare_sockaddr()`, `from_local()`), and `xlog`. It integrates with RPC service setup as a caller authorization filter.

Risks: the cache key includes program but lookup only compares socket address, so different program decisions in the same hash bucket can collide logically. `check_files()` returns unchanged when either hosts file is missing, so policy file creation/removal edge cases deserve scrutiny. No locking protects the global cache, so multithreaded callers could race. `strncpy()` fallback may omit a NUL if buffer sizing changes, though current call uses a sufficiently large fixed buffer.

Test signals: exercise IPv4/IPv6 address formatting, hosts file mtime invalidation, local bypass, remote allow/deny, repeated cached calls, missing hosts files, and concurrent access if used in threaded daemons.
