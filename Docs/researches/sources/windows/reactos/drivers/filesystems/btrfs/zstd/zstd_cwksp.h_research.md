# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_cwksp.h

## Summary
Defines `ZSTD_cwksp`, zstd's compact workspace arena used by compression contexts to pack fixed objects, buffers, aligned scratch areas, and hash/chain tables into a single allocation.

## Key APIs
- Workspace lifecycle: `ZSTD_cwksp_init()`, `ZSTD_cwksp_create()`, `ZSTD_cwksp_free()`, `ZSTD_cwksp_move()`, `ZSTD_cwksp_sizeof()`.
- Allocation helpers: `ZSTD_cwksp_reserve_object()`, `ZSTD_cwksp_reserve_buffer()`, `ZSTD_cwksp_reserve_aligned()`, `ZSTD_cwksp_reserve_table()`.
- State helpers: `ZSTD_cwksp_clear()`, `ZSTD_cwksp_clear_tables()`, `ZSTD_cwksp_clean_tables()`, `ZSTD_cwksp_mark_tables_dirty()`, `ZSTD_cwksp_mark_tables_clean()`.
- Capacity helpers: `ZSTD_cwksp_available_space()`, `ZSTD_cwksp_check_available()`, oversized/waste checks.

## Important Behavior
The arena layout grows objects and tables upward from the bottom while buffers/aligned allocations grow downward from the top. Allocation order is enforced through phases: objects, buffers, aligned allocations, then tables. Tables have a validity boundary so compression match tables can be reused when their entries are known to remain bounded, or partially zeroed when dirty.

Under AddressSanitizer and MemorySanitizer builds, the workspace inserts or poisons regions to catch intra-workspace overflows and stale reads. Static objects remain valid across `ZSTD_cwksp_clear()`, while buffers/aligned/table allocations are invalidated.

## Risks
Misordered reservations set `allocFailed` or assert in debug builds. Table reuse depends on correct dirty/clean marking by callers; stale table ranges could corrupt match finding if a caller skips the expected cleanup path. Pointer arithmetic assumes correctly aligned workspace starts.
