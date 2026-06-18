# sources/storage-engines/foundationdb/flow/include/flow/Histogram.h

## Purpose
`Histogram.h` defines Flow's lightweight power-of-two and linear bucket histogram support plus a registry for trace reporting.

## Important APIs, Types, And Functions
Important types are `HistogramRegistry` and `Histogram`. APIs include `GetHistogramRegistry()`, registry register/unregister/lookup/log/clear, `Histogram::getHistogram()`, `sample()`, `sampleSeconds()`, `samplePercentage()`, `sampleRecordCounter()`, `updateUpperBound()`, `clear()`, `writeToLog()`, `name()`, and `drawHistogram()`.

## Control Flow
`getHistogram()` looks up `group:op` in the global registry, creating and registering a histogram if absent. Samples map to one of 32 buckets by bit scan, percentage step, or linear interpolation. Destruction unregisters active histograms.

## State And Persistence Behavior
Registry state is an ordered map from names to histogram pointers. Each histogram stores group/op/unit, bounds, a registry reference, and 32 counters. Buckets persist until cleared, logged, or object destruction.

## Dependencies And Integration Points
It depends on `Arena`, `ReferenceCounted`, `Reference`, platform bit operations, and Trace logging in implementation. `Net2Packet` uses a histogram for unsent packet queue latency.

## Risks And Edge Cases
`sampleRecordCounter()` divides by `upperBound - lowerBound`, so equal bounds are dangerous despite constructor only checking `>=`. Registry raw pointers require unregister on destruction. Concurrent sampling/registry changes need external synchronization if used off the main thread.

## Test Signals
Bucket mapping tests, zero sample behavior, percentage clamp, linear bounds, registry reuse/unregister, log formatting, draw output, and Windows/non-Windows bit-scan builds are relevant.
