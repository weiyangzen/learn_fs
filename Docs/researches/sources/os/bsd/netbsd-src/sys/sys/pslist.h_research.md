# File Research: sources/os/bsd/netbsd-src/sys/sys/pslist.h

## Purpose
Provides a passive-serialization-friendly singly linked list with writer and reader operations, atomic publication, poisoning, and type-safe container macros.

## Main API
- Structures: `struct pslist_head`, `struct pslist_entry`.
- Initialization/destruction: `pslist_init`, `pslist_destroy`, `pslist_entry_init`, `pslist_entry_destroy`.
- Writer operations: insert head/before/after, remove, first/next.
- Reader operations: first/next with consume loads.
- Convenience macros: `PSLIST_INIT`, `PSLIST_ENTRY_INIT`, `PSLIST_WRITER_INSERT_*`, `PSLIST_WRITER_REMOVE`, `PSLIST_WRITER_FOREACH`, `PSLIST_READER_FOREACH`.

## Dependencies
Uses `sys/param.h` and atomic operations. Kernel assertions map to `KASSERT`; userland maps to `assert`.

## Risks and Notes
Writers must exclude other writers but not readers. After writer removal, `ple_next` is intentionally left intact until readers drain; callers must use a grace mechanism such as `pserialize_perform` before destroying or reusing entries.
