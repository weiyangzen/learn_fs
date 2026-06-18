# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_dtablesize.c

Read completely: 61 lines.

Implements `_rpc_dtablesize()`, a small helper that caches `sysconf(_SC_OPEN_MAX)` in a static integer and returns it on later calls.

This avoids repeated syscalls for legacy RPC code that needs the process descriptor table size. There is no locking; benign races can only recompute the cached value.
