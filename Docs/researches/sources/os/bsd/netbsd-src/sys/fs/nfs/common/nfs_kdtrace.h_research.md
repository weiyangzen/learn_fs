# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_kdtrace.h

This header provides optional KDTrace/DTrace probe wrappers for NFS client access-cache and attribute-cache events.

Key contents:
- Under `KDTRACE_HOOKS`, declares probe IDs for access-cache flush, get-hit, get-miss, and load-done events.
- Defines macros that call registered DTrace probe function pointers only when non-null.
- Provides matching attr-cache probe macros.
- When `KDTRACE_HOOKS` is absent, all macros compile to no-ops.

Important dependencies:
- Includes `sys/dtrace_bsd.h` only when tracing is enabled.
- Probe function pointers are expected from the tracing subsystem.

Risks and notes:
- This is instrumentation-only and should not alter behavior when disabled.
