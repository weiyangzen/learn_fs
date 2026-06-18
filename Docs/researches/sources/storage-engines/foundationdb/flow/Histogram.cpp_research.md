# sources/storage-engines/foundationdb/flow/Histogram.cpp

## Purpose
Implements Flow histogram registry lookup, registration, logging, clearing, text drawing, and a smoke test.

## Important APIs, Types, And Functions
`GetHistogramRegistry()` stores a singleton registry in `g_network->global(INetwork::enHistogram)`. `HistogramRegistry::{registerHistogram, unregisterHistogram, lookupHistogram, logReport, clear}` manage live histograms. `Histogram::writeToLog(double)` emits bucketed TraceEvents and resets buckets. `Histogram::drawHistogram()` renders an ASCII/Unicode bar chart.

## Control Flow
Histogram logging first checks whether any of 32 buckets are active. Active histograms emit group/op/unit/elapsed and bucket fields formatted by unit type, then `clear()`. Registry unregister requires exactly one erased entry. The smoke test samples byte and millisecond histograms, forces reports, verifies reset/deallocation behavior, and calls report after deallocation.

## State And Persistence Behavior
The registry is process/network-global, scoped through `g_network`. Histograms hold bucket counters until logged or cleared. Persistence is limited to TraceEvent output.

## Dependencies And Integration Points
Depends on `flow/Histogram.h`, `flow/flow.h`, `UnitTest`, `TraceEvent`, and `INetwork` global storage. Comments note a Flow/fdbrpc coupling around simulation scoping.

## Risks And Edge Cases
`drawHistogram()` divides by total without checking zero, so callers should use it only for non-empty histograms. Duplicate/missing registration is treated as serious. Unit-specific bucket names are part of trace parsing compatibility.

## Test Signals
`/flow/histogram/smoke_test` validates sampling bucket placement, log reset, registry lifecycle, and report after deallocation.
