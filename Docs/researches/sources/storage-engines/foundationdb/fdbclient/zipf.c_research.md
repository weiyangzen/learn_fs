# sources/storage-engines/foundationdb/fdbclient/zipf.c

## Purpose
This C file implements the YCSB-derived Zipfian integer generator declared in `zipf.h`. It produces skewed integer samples over a configured inclusive range.

## Important APIs, Types, And Functions
Public functions are `zipfian_generator3`, `zipfian_generator`, and `zipfian_next`; internal helpers include `zipfian_generator4`, `zipfian_generator2`, `next_int`, `rand_double`, `zetastatic2`, `zeta2`, `zetastatic`, and `zeta`. Global static variables hold item count, base, theta/alpha/zeta values, and count tracking.

## Control Flow
Initialization computes `items`, `base`, `theta`, `zeta2theta`, `alpha`, `zetan`, `countforzeta`, and `eta`, then calls `zipfian_next()` once to warm the generator. `zipfian_next` delegates to `next_int(items)`. `next_int` updates zeta if item count changed, draws `u = rand()/RAND_MAX`, handles the first two high-probability items specially, and otherwise computes the selected item with the Zipfian power formula.

## State And Persistence Behavior
All generator state is process-global and mutable. There is no persistence, no per-instance object state, and no locking. Randomness comes from the C library `rand()` global state; this file does not seed it.

## Dependencies And Integration Points
It depends on `<math.h>`, `<stdlib.h>`, and `fdbclient/zipf.h`. It is suitable for benchmark/test code that can tolerate global generator state.

## Risks And Edge Cases
The implementation is not thread-safe or reentrant. Invalid ranges, zero item counts, or `zipfianconstant` values near 1 can produce division/power edge cases. `allowitemcountdecrease` is always zero, so decreasing item counts do not recompute zeta through that branch. The disabled test block calls `next_value()`, which is not defined, indicating stale sample code.

## Test Signals
Tests should assert generated values stay within `[min,max]`, repeated initialization resets bounds, distribution is skewed toward low ranks, deterministic behavior follows `srand`, and concurrent use is either avoided or explicitly documented as unsafe.
