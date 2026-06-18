# File Research: sources/os/bsd/openbsd-src/sys/sys/memrange.h

Defines `/dev/mem` memory range attribute ioctl ABI and kernel backend hooks.

Key contents:
- Memory attribute flags for uncacheable, write-combine, write-through, write-back, write-protect, unknown, fixed, firmware, active, bogus, fixed-active, and force.
- `struct mem_range_desc`: base, length, flags, and owner label.
- `struct mem_range_op`: descriptor pointer and operation args.
- Ioctls `MEMRANGE_GET` and `MEMRANGE_SET`.
- `MEMRANGE_WC_RANGE` offset marker for write-combining mappings.

Kernel integration:
- `struct mem_range_ops` backend callbacks for init, set, AP init, and reload.
- `mem_range_softc` global and attach/get/set/AP/reload functions.

Risk notes:
- The ABI allows forced risky cache-attribute changes; machine-dependent implementations must validate ranges carefully.
