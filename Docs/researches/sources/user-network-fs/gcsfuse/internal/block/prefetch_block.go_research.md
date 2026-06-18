<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go

Purpose: extends memory blocks with absolute file offsets, readiness notification, status, reference counting, and efficient `ReaderFrom` support for buffered read prefetching.

Important APIs/types/functions: `BlockStatus`, `BlockState`, `PrefetchBlock`, `prefetchMemoryBlock`, `createPrefetchBlock`, `ReadAt`, `ReadAtSlice`, `AbsStartOff`, `SetAbsStartOff`, `AwaitReady`, `NotifyReady`, `IncRef`, `DecRef`, `RefCount`, and `ReadFrom`.

Control flow: created/reused blocks start in-progress with a one-shot notification channel and unset offset. Producers write data then `NotifyReady`; consumers `AwaitReady`, then read slices or copied bytes. Reference counts prevent returning blocks to the pool while FUSE still owns returned slices.

State and persistence: all state is in memory. The backing buffer is mmap memory inherited from `memoryBlock`; readiness and ref-count fields are reset on reuse.

Dependencies: context cancellation for waits, atomic ref-counting, syscall mmap, and buffered-reader lifecycle rules that call notify exactly once.

Risks: double `NotifyReady` panics or blocks; `AbsStartOff` panics before initialization; `DecRef` panics on imbalance. Returned slices must not be mutated and require callback-based lifetime management.

Test signals: `prefetch_block_test.go` covers read bounds, offset setting, notification variants, cancellation, ref counting, and `ReadFrom` edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block.go -->
