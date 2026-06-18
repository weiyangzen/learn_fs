# File Research: sources/os/bsd/freebsd-src/sys/sys/vmem.h

Extent/arena allocator interface for virtual or resource address ranges.

Key responsibilities:
- Defines opaque `vmem_t`, address and size types, minimum/maximum address constants, and utilization typemask bits.
- Defines import, release, and reclaim callback types.
- For non-kernel builds, defines M_* allocation flags needed by vmem userspace consumers.
- Declares create/init/destroy, import callback setup, size limit setup, reclaim callback setup, normal allocation/free, constrained allocation/free, static span add, quantum-size roundup, utilization query, diagnostic lookup/printing, print-all, and startup functions.
- Documents allocation policies such as first fit, best fit, next fit, blocking behavior, quantum caches, alignment, phase, no-cross boundaries, and min/max constraints.

Dependencies:
- Includes `sys/types.h`.

Notable risks:
- `vmem_xalloc()` constraint semantics are subtle: min/max apply to last/first bytes as documented, not just starting address.
- Normal allocation/free honor quantum caches, while constrained allocation bypasses them; callers must choose the right path for alignment-sensitive resources.
