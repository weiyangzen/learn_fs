# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nsdispatch.c

NetBSD libc name-service switch dispatcher. It maintains global database-to-source maps and loaded NSS modules, with default source lists for `files`, `compat`, and `nis` variants.

`_nsconfigure()` watches `_PATH_NS_CONF`, parses it with the lexer/parser, rebuilds the map/module arrays, and sorts them for binary search. Threaded builds use a read/write lock plus a per-thread recursion list so recursive `nsdispatch()` calls do not attempt configuration reloads while holding a read lock.

`nsdispatch()` selects the configured source list or caller defaults, resolves a callback from the caller’s dispatch table or dynamic `nss_*.so` modules, passes variadic arguments to the method, and stops based on the source’s status flags unless force-all behavior is requested.
