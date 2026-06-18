# File Research: sources/os/plan9/9front/sys/src/9/ppc/devflash.c

Plan 9 `#F` flash-memory device for CFI flash parts.

Key responsibilities:
- Handles 8-bit or 16-bit flash widths and optional interleaving through compile-time macros.
- Queries CFI data, records algorithm ID, total size, write-buffer size, and erase-region geometry.
- Supports Intel/Sharp Extended command set identification, erase, and buffered writes.
- Provides placeholder AMD/Fujitsu identification but erase/write return unimplemented errors.
- Exposes flash partitions and partition control files through the Plan 9 device interface.
- Supports partition add/remove, whole-partition or single-block erase, boot-block protection toggling, and data reads/writes.
- Enforces eve-only access for opening and data operations.

Dependencies:
- Uses `isaconfig("flash", ...)`, board `flashprogpower()`, Plan 9 device-walk/read/write helpers, and block-boundary geometry.

Notable behavior:
- Writes are copied into kernel memory first to avoid faults during flash programming, padded to word boundaries, split at erase-block and `Maxwchunk` limits, then verified with `memcmp()`.
- Boot protection rejects writes/erases in the first erase block unless disabled through `protectboot off`.
