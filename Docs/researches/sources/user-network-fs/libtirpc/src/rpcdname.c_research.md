<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcdname.c -->
# sources/user-network-fs/libtirpc/src/rpcdname.c

Purpose: returns the system default NIS/RPC domain name through a small caching wrapper.

Important APIs and functions: internal `get_default_domain()` calls `getdomainname()` into a stack buffer and stores a heap copy in static `default_domain`. `__rpc_get_default_domain(char **domain)` exposes the cached string and returns `0` on success or `-1` on failure.

Control flow: first successful call reads the domain, rejects empty strings, allocates and copies it, then returns the cached pointer. Later calls return the cached pointer without another syscall.

State and persistence: `default_domain` is process-global, heap allocated, and never freed. The returned pointer is shared and should not be modified or freed by callers.

Dependencies and integration points: used by NIS/RPC name code that needs a default domain and expects ypclnt-style success/failure status.

Risks: no locking protects first-time initialization, so concurrent first calls can race and leak or publish one of multiple allocations. The 256-byte temporary buffer truncation behavior depends on `getdomainname`.

Test signals: empty domain failure, successful cached domain reuse, concurrent first-call stress, and callers treating returned memory as read-only shared storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcdname.c -->
