# File Research: sources/os/bsd/freebsd-src/sys/sys/memrange.h

Defines memory range attribute ioctls and kernel hooks for `/dev/mem`.

Key content:
- Memory attribute flags represent uncacheable, write-combine, write-through, write-back, write-protect, unknown, and attribute mask.
- Control flags identify fixed base/length, firmware-provided, active, bogus, fixed active, busy, and force.
- `struct mem_range_desc` describes base, length, flags, and owner string.
- `struct mem_range_op` carries descriptor pointer and operation args for update/remove.
- Ioctls: `MEMRANGE_GET`, `MEMRANGE_SET`.
- `struct mem_extract` supports virtual-to-physical extraction with domain and state; ioctl `MEM_EXTRACT_PADDR`.
- `struct mem_livedump_arg` supports live kernel dump request; ioctl `MEM_KERNELDUMP`.
- Kernel-only declarations include `M_MEMDESC`, `struct mem_range_ops`, `struct mem_range_softc`, global `mem_range_softc`, init/destroy, and get/set attribute APIs.

Research relevance:
- Relevant to low-level memory mapping, caching behavior, kernel dumps, and physical address inspection.
- Storage and filesystem crash/debug workflows may use live dump and memory extraction paths.

Cautions:
- Attribute modifications can be risky; `MDF_FORCE` exists for risky changes.
- Machine-dependent implementation is abstracted behind `mem_range_ops`.
