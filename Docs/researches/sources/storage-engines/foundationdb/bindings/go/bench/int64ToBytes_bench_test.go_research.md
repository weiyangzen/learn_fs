# sources/storage-engines/foundationdb/bindings/go/bench/int64ToBytes_bench_test.go

## Purpose

This benchmark compares two ways to convert an `int64` to an eight-byte little-endian representation in Go. It is a focused performance microbenchmark relevant to FoundationDB atomic integer operations and allocator counters, where byte encoding is frequent and allocation behavior matters.

## Important APIs, Types, and Functions

`Benchmark_Int64ToBytesBuffer` allocates a new `bytes.Buffer` each iteration and writes the integer via `binary.Write` with `binary.LittleEndian`. `Benchmark_Int64ToBytesPut` allocates a fixed eight-byte slice and writes with `binary.LittleEndian.PutUint64`. The package-level `result []byte` retains the last generated slice so the compiler cannot fully eliminate the work.

Both benchmarks call `b.ReportAllocs()` and `b.SetBytes(...)`, making benchmark output include allocation counts and throughput based on encoded byte length.

## Control Flow

Each benchmark loops over `b.N`, encodes `n`, updates the benchmark byte count, stores the current result in a local variable, and assigns it to the global sink after the loop. The buffer variant handles and reports a possible `binary.Write` error; the direct slice variant has no fallible operation.

## State and Persistence Behavior

There is no persistent state. Runtime state is limited to heap allocations made during the benchmark and the final assignment to `result`. The benchmark intentionally observes allocation behavior.

## Dependencies and Integration Points

The file depends only on the Go standard library packages `bytes`, `encoding/binary`, and `testing`. It is independent from the FoundationDB client runtime, but its result can inform low-level binding implementation choices where little-endian integer bytes are needed.

## Risks

The benchmark allocates a new slice even in the direct `PutUint64` path, so it compares API overhead plus one allocation rather than a fully allocation-free reusable buffer strategy. Repeated `b.SetBytes` inside the loop is unusual; it is stable here because the encoded size is constant but still adds benchmark bookkeeping overhead.

## Test Signals

Run with `go test -bench .` from the benchmark package. Expected signal is lower allocations and better throughput for the direct `PutUint64` path compared with `bytes.Buffer` plus `binary.Write`.
