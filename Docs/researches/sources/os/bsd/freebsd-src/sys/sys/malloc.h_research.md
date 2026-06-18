# File Research: sources/os/bsd/freebsd-src/sys/sys/malloc.h

Defines FreeBSD kernel malloc type accounting, allocation flags, allocator APIs, and standalone fallback allocation macros.

Key content:
- Allocation flags include `M_NOWAIT`, `M_WAITOK`, `M_NORECLAIM`, `M_ZERO`, `M_NOVM`, `M_USE_RESERVE`, `M_NODUMP`, fit strategies, executable allocation, never-freed, and unprotected allocation.
- `M_VERSION` guards malloc type structure versioning.
- `struct malloc_type_stats` stores per-CPU allocation/free counters and size bitmask; asserted to be 64 bytes.
- `struct malloc_type_internal` stores DTrace probes, UMA zone id, per-CPU stats, and spare ABI fields.
- `struct malloc_type` is the public type descriptor with global-chain link, version, short description, and internal data.
- Stream structures expose `kern.malloc` statistics to userland.
- Kernel macros `MALLOC_DEFINE` and `MALLOC_DECLARE` define/register malloc types via SYSINIT/SYSUNINIT.
- Declares common malloc types such as `M_CACHE`, `M_DEVBUF`, `M_TEMP`, and `M_IOV`.
- Declares allocation APIs including `malloc`, `free`, `zfree`, `realloc`, `reallocf`, `mallocarray`, domainset variants, executable variants, aligned variants, and contiguous allocation.
- The `malloc` macro optimizes compile-time-known `M_ZERO` allocations by clearing at the call site.
- `WOULD_OVERFLOW()` supports multiplication overflow detection for array allocation.
- `_STANDALONE` maps allocation to boot/stand `Malloc`/`Free`.

Research relevance:
- This is the core allocator contract for kernel subsystems, including VFS, modules, mbuf tags, mount state, and device ioctls.
- Malloc type accounting is important when tracing memory use by filesystem components.

Cautions:
- Kernel `malloc` is macro-wrapped, so call-site behavior may differ from a plain function call.
- Struct layout is ABI-sensitive for monitoring tools.
