# File Research: sources/os/bsd/netbsd-src/sys/sys/asan.h

Read completely: 86 lines.

Defines the NetBSD kernel address sanitizer interface.

When `KASAN` is enabled:
- Includes required kernel type and bus headers.
- Defines compiler ABI shadow scale shift.
- Defines stack redzone marker values for left/mid/right redzones, use-after-return, and use-after-scope.
- Defines NetBSD redzone markers for generic, malloc, kmem, pool, and freed pool memory.
- Defines DMA marking types for linear, mbuf, uio, and raw DMA.
- Declares initialization, shadow mapping, softint, DMA sync/load, redzone sizing, and memory marking functions.

When `KASAN` is disabled:
- Exposes no-op macros for the same API so call sites compile away.

Risks and notes:
- Several constants are part of the compiler ABI and must match instrumentation expectations.
- The disabled path depends on `__nothing` semantics to remove side effects.
