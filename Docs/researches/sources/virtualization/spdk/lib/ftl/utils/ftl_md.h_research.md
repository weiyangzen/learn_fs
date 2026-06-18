# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_md.h

Public metadata object API and type definitions.

Defines:
- `struct ftl_md` ownership, buffers, IO state, SHM state, mirror flags.
- `union ftl_md_vss` fixed 64-byte metadata variants for version, trim, P2L checkpoint, and NV cache.
- Create/destroy flags.
- Restore, persist, clear, full-buffer access, VSS allocation, entry read/persist, transfer sizing, and region SHM flag helpers.

Contract:
- Callers set `md->cb` and owner context before async operations.
- Entry operations require `region->entry_size` to be set.
