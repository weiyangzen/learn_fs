# File Research: sources/os/bsd/freebsd-src/sys/sys/_align.h

Small alignment macro header.

Defines:
- `_ALIGNBYTES` as `sizeof(void *) - 1`.
- `_ALIGN(p)` as `__align_up((p), _ALIGNBYTES + 1)`.

Important note:
- The header explicitly documents these interfaces as obsolete/ambiguous and recommends `alignof(type)` plus `__align_up()` for new code.
- CHERI/provenance concerns are called out: `_ALIGN()` preserves type and provenance, which matters for kernel file descriptor passing.

Research relevance:
- Foundational ABI-style macro used by old interfaces needing pointer-sized alignment.
