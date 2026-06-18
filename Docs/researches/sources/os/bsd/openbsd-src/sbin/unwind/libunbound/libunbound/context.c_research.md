# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.c

`context.c` implements internal libunbound context setup, outstanding-query bookkeeping, allocator-cache reuse, and pipe-message serialization/deserialization for background asynchronous resolution.

`context_finalize()` applies runtime configuration, initializes module startup/init, creates local zones, applies local/auth-zone/forward/hint/EDNS-string configuration, sizes message/rrset/infra caches, sets logging, and marks the context finalized. After this point many public configuration calls reject changes with `UB_AFTERFINAL`.

The query registry uses an rbtree keyed by integer query IDs. `context_new()` allocates `ctx_query`, assigns an unused ID, creates the user-facing `ub_result`, records callback metadata, and inserts the query. `context_query_delete()` frees query result/message storage. `find_id()` retries query-ID allocation up to `NUM_ID_TRIES`.

The serialization protocol supports `UB_LIBCMD_NEWQUERY`, `UB_LIBCMD_CANCEL`, `UB_LIBCMD_ANSWER`, and `UB_LIBCMD_QUIT`. Messages encode fixed-width command/query/type/class/error/security fields followed by query names, optional bogus-reason strings, and raw DNS answer packets. Deserializers validate minimum lengths and look up existing queries before attaching results or cancellations.
