<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_dtablesize.c -->
# sources/user-network-fs/libtirpc/src/rpc_dtablesize.c

Purpose: supplies `_rpc_dtablesize()`, a cached descriptor-table size for select-based service loops.

Important APIs and functions: `_rpc_dtablesize()` calls `sysconf(_SC_OPEN_MAX)` once, clamps the value to `FD_SETSIZE`, caches it in a static `size`, and returns it thereafter.

Control flow: first call populates the static cache; later calls return it directly. If `sysconf` returns a value larger than `FD_SETSIZE`, the function returns `FD_SETSIZE` because `fd_set` cannot represent higher descriptors.

State and persistence: one process-local static integer persists after first use. It is not refreshed if resource limits change later.

Dependencies and integration points: used by `svc.c` to size `__svc_xports` and scan fd sets. It includes public RPC compatibility headers.

Risks: `sysconf(_SC_OPEN_MAX)` failure is not explicitly handled; a negative return could be cached and later used incorrectly. The cache can become stale after `setrlimit`.

Test signals: run under normal and low/high `RLIMIT_NOFILE` settings, validate clamping to `FD_SETSIZE`, and exercise service registration after changing limits to document static-cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_dtablesize.c -->
