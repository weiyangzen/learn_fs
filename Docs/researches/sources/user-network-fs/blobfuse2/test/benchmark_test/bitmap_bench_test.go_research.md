<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go

## Purpose
Microbenchmarks comparing atomic 64-bit bitmap operations with simple 16-bit bitmap operations.

## Important APIs, Types, and Functions
`BitMap64` implements `IsSet`, `Set`, `Clear`, and `Reset` using `sync/atomic` load/CAS loops. `BitMap16` implements equivalent non-atomic operations. Benchmarks cover set, is-set, clear, reset, and parallel set for both types.

## Control Flow and State
Each benchmark initializes a bitmap, resets the timer, then runs repeated operations with bit indices masked into valid ranges. Parallel benchmarks use `b.RunParallel` and shared bitmap state.

## Dependencies and Integration Points
Uses Go `testing` benchmark framework and `sync/atomic`. This appears to benchmark candidate implementations rather than directly importing production bitmap code.

## Risks and Edge Cases
`BitMap16_Set_Parallel` mutates shared non-atomic state in a parallel benchmark, producing a data race under `-race`; that may be intentional for comparison but is unsafe. `Set` and `Clear` benchmarks saturate state quickly, so many iterations measure already-set/already-cleared fast paths. It is not a correctness test.

## Test Signals
`go test bitmap_bench_test.go -bench=. -benchmem` reports allocation and timing comparisons for bitmap strategies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go -->
