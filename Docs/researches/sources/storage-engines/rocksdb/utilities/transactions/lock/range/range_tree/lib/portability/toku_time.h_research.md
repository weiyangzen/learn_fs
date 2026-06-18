# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_time.h

## Purpose
Provides Toku-style timing primitives for the locktree code, especially cheap performance timestamps and wall-clock microsecond time.

## Important APIs, Types, And Functions
`tokutime_t` is a `uint64_t` performance timestamp. `toku_time_now()` reads an architecture-specific cycle or timebase register. `toku_current_time_microsec()` uses `gettimeofday` and returns microseconds since the Unix epoch.

## Control Flow
`toku_time_now()` is a compile-time architecture switch: x86 uses `rdtsc`, AArch64 reads `cntvct_el0`, PowerPC uses `__ppc_get_timebase`, s390x uses `stckf`, RISC-V uses `rdcycle`, and LoongArch uses `rdtime.d`. Unsupported architectures fail compilation. Wall-clock microseconds are fetched through `gettimeofday`.

## State And Persistence Behavior
No state is stored. Values are transient timing samples used by status counters and wait/escalation timing.

## Dependencies And Integration Points
Depends on system time headers and architecture intrinsics/assembly. Locktree status and lock wait paths use these values for elapsed-time statistics. Comments note RocksDB `Env::NowMicros()` and `NowNanos()` as possible substitutes.

## Risks And Edge Cases
Cycle counters are not portable wall-clock time and can vary by architecture, CPU frequency behavior, or virtualization. `gettimeofday` can move backward if system time changes. The hard `#error` on unsupported platforms makes this header a portability gate for range-tree locking.

## Test Signals
Compile coverage across supported architectures is important. Runtime tests should only compare elapsed differences, not absolute `tokutime_t` values. Lock wait and escalation counters are indirect behavioral signals.
