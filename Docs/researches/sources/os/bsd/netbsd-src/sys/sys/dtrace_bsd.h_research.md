# File Research: sources/os/bsd/netbsd-src/sys/sys/dtrace_bsd.h

Provides BSD/NetBSD shim declarations for imported DTrace code and kernel hook integration.

Key content:
- Includes kernel, memory, proc, and DTrace option headers.
- Cyclic clock hook type and array.
- Trap/invop/doubletrap hook types and globals.
- Virtual time switch hook.
- Fasttrap fork/exec/exit hooks.
- `dtmalloc` probe hook.
- NFS client DTrace provider hooks for access cache, attribute cache, and NFSv2/v3 RPC events.
- `dtrace_gethrtime`, `dtrace_gethrestime`.
- Fixed DTrace process/thread opaque storage sizes.
- Inline constructors/destructors allocating/freeing `p_dtrace` and `l_dtrace` when `KDTRACE_HOOKS` is enabled.

Important behavior:
- Wraps optional instrumentation so core proc/lwp lifecycle can support DTrace without always allocating storage.
- Intended for kernel-only DTrace integration.
