# File Research: sources/os/bsd/netbsd-src/sys/sys/vmem_impl.h

Read completely: 159 lines.

Private data structures for the `vmem` allocator implementation. It defines arenas, boundary tags, freelist/hash/list heads, optional quantum-cache backing, and internal initialization helpers.

Core structures:
- `struct vmem` holds locks/CV, flags, import/release functions, free boundary-tag pool, segment list, power-of-two freelists, busy-tag hash table, quantum parameters, arena size/in-use accounting, name, all-arena linkage, and optional qcache state.
- `struct vmem_btag` represents spans/free/busy extents with segment-list linkage, freelist or hash-list linkage, start, size, type, and flags.
- Boundary tag types distinguish dynamic/static spans, free extents, and busy extents.

Kernel versus standalone:
- Kernel builds enable `QCACHE`, include pools, and use `kmutex_t`/`kcondvar_t`.
- Non-kernel builds use libc/assert/errno headers and compile lock/CV declarations away.

Risks and notes:
- Boundary-tag accounting is central to correctness; corrupt tag type/list membership would affect allocator state globally.
- `VMEM_EST_BTCOUNT` documents the expected metadata pressure: roughly two tags per allocation plus two per span.
