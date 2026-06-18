# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/zipf.h

## Purpose
This header exposes a small C ABI for a YCSB-derived Zipfian integer generator used by FoundationDB client-side tests or benchmarks that need skewed key selection. It defines `ZIPFIAN_CONSTANT` as `0.99`, declares generator initialization overloads, and declares `zipfian_next()` for producing the next sampled item.

## Important APIs, Types, And Functions
The public API is `zipfian_generator3(int min, int max, double zipfianconstant)`, `zipfian_generator(int items)`, and `zipfian_next()`. The declarations are wrapped in `extern "C"` for C++ consumers and protected by both `#ifndef ZIPF_H` and `#pragma once`.

## Control Flow
Callers must initialize process-global generator state with either an item count or an explicit min/max/constant range before calling `zipfian_next()`. The header itself has no logic; it couples callers to the global-state implementation in `zipf.c`.

## State And Persistence Behavior
No persistent state is declared here. The important state implication is that the implementation uses global static state, so this header represents a singleton generator rather than a reusable object.

## Dependencies And Integration Points
The header integrates C and C++ code by providing C linkage. It is included by `zipf.c` and any workload or benchmark code needing YCSB-like distributions.

## Risks And Edge Cases
The API does not expose seeding, reset, thread-safety, or error handling. Calling `zipfian_next()` before initialization, using invalid ranges, or sharing the generator across threads depends entirely on implementation behavior.

## Test Signals
Useful tests initialize with known item counts/ranges, assert samples remain within bounds, compare histogram skew, and check that C++ code can link through the C ABI.
