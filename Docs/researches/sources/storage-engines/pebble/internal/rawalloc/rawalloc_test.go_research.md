# sources/storage-engines/pebble/internal/rawalloc/rawalloc_test.go

## Purpose
This file benchmarks uninitialized allocation against ordinary zeroed `make` allocation across several buffer sizes.

## Important APIs, Types, and Functions
`sizes` lists buffer sizes from 16 bytes through 1 MiB. `BenchmarkRawalloc` calls `New(size,size)` in a loop. `BenchmarkMake` calls `make([]byte,size)` in a loop.

## Control Flow and State
Each benchmark iterates over sizes and creates a sub-benchmark per size. Allocated slices are discarded immediately, so the benchmark primarily measures allocation and zeroing overhead as seen by the compiler/runtime.

## Dependencies and Integration
The file uses `fmt` and `testing`. It provides performance evidence for the risky `rawalloc` implementation.

## Risks and Gaps
The benchmarks do not prevent compiler/runtime optimizations beyond assigning to blank identifier, so results should be interpreted carefully. There are no tests that verify length/capacity, GC safety, or expected non-zero contents.

## Test Signals
The size range signals that raw allocation is intended to help with medium-to-large scratch buffers, not only tiny allocations.
