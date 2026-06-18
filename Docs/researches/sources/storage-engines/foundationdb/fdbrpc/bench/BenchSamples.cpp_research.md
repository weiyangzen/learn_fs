# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSamples.cpp

## Purpose
`BenchSamples.cpp` benchmarks sampling and histogram primitives used by fdbrpc metrics: DDSketch variants, `ContinuousSample`, `LatencyBands`, and Flow `Histogram`.

## Important APIs, Types, and Functions
Benchmarks include `bench_ddsketchUnsigned`, `bench_ddsketchInt`, `bench_ddsketchDouble`, `bench_ddsketchLatency`, `bench_continuousSampleInt`, `bench_continuousSampleLatency`, `bench_latencyBands`, `bench_histogramInt`, `bench_histogramPct`, and `bench_histogramTime`. `InputGenerator<T>` supplies precomputed random inputs.

## Control Flow
Each benchmark constructs the target sampler and an input generator, then loops over Google Benchmark iterations adding one sample per iteration. DDSketch benchmarks run at several error guarantees; continuous sample benchmarks run at different reservoir sizes; latency bands create thresholds before measurement.

## State and Persistence Behavior
All state is in-memory inside sampler objects. Histograms are obtained through `Histogram::getHistogram`, which may use process-global histogram registries. No durable output is produced.

## Dependencies and Integration Points
It depends on Google Benchmark, `BenchSupport.h`, `fdbrpc/Stats.h`, `fdbrpc/DDSketch.h`, `ContinuousSample.h`, `flow/Histogram.h`, and deterministic random support. It exercises the metric data structures used by runtime tracing and telemetry.

## Risks and Edge Cases
Precomputed random input avoids measuring random generation in the hot loop but uses deterministic global random during setup. Some benchmarks reuse the same sampler across all iterations, so bucket growth or saturation is part of the measurement. `bench_latencyBands` passes `false` as the third argument to `addMeasurement`, relying on bool conversion to the `Filtered` enum/type.

## Test Signals
Signals are throughput, aggregate timing, and successful execution without sampler assertions. They are performance tests rather than accuracy tests.
