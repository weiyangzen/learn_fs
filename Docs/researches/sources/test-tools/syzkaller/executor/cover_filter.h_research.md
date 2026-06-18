# sources/test-tools/syzkaller/executor/cover_filter.h

Purpose: Shared-memory PC membership filter used to suppress already-known signal and restrict coverage to interesting code regions.

Important APIs and control flow: `CoverFilter()` allocates a new `ShmemFile`; `CoverFilter(fd, preferred)` maps an existing filter, usually in an executor child. `Insert` calls `FindByte(pc, true)` and sets a bit. `Contains` calls `FindByte(pc, false)`. `Seal` makes the shared mapping read-only and closes its fd. The table supports up to four 1 GiB regions, L1 entries per 1 MiB chunk, and L2 16 KiB bitmaps that drop the low three PC bits.

State and dependencies: the serialized `Table` lives entirely in shared memory, while `alloc_` is process-local allocation state for new L2 blocks. Filters passed to children are sealed or treated read-only, so only the creator should insert after construction. Depends on `ShmemFile`, `failmsg`, and executor integer typedefs.

Integration points: runner builds `max_signal_` and `cover_filter_`, passes their fds to child executors, and executor-side `coverage_filter` queries them while writing signal/coverage/comparisons.

Risks and tests: false positives are intentional from 8-byte granularity. Overflow is fatal when more than four regions or the bitmap budget is exceeded. `test_cover_filter` validates parent/child shared visibility, region boundaries, low-bit coalescing, and negative cases.
