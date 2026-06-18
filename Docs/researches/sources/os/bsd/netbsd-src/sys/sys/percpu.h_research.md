# File Research: sources/os/bsd/netbsd-src/sys/sys/percpu.h

## Purpose
Declares NetBSD per-CPU storage allocation, traversal, and callback APIs.

## Main API
- Initialization: `percpu_init`, `percpu_init_cpu`.
- Allocation: `percpu_alloc`, `percpu_free`, `percpu_create`.
- Current CPU access: `percpu_getref`, `percpu_putref`.
- Traversal: `percpu_foreach`, `percpu_foreach_xcall`.
- Low-level traversal/access: `percpu_traverse_enter`, `percpu_traverse_exit`, `percpu_getptr_remote`.
- Callback type: `percpu_callback_t`.

## Dependencies
Includes `sys/percpu_types.h`.

## Risks and Notes
Callers must pair `percpu_getref` with `percpu_putref`. Remote pointer access is explicitly low-level and should be reserved for cases that can satisfy traversal and CPU-lifetime constraints.
