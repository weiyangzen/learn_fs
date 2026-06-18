# sources/storage-engines/foundationdb/contrib/ddsketch_calc.py

## Purpose
Implements DDSketch bucket mapping math using cubic interpolation for fast log and inverse log calculations.

## Important APIs, Types, And Functions
`DDSketch` exposes constructor `DDSketch(errorGuarantee)`, `fastlog(value)`, `reverseLog(index)`, `getIndex(sample)`, and `getValue(idx)`. Constants `A`, `B`, `C`, `EPS`, `correctingFactor`, `offset`, `multiplier`, and `gamma` define the mapping.

## Control Flow
Construction derives `gamma`, `multiplier`, and offset based on the requested relative error. `getIndex()` approximates log2 of a sample and maps it to a bucket. `getValue()` reverses the mapping with cubic root math and adjusts by `gamma`.

## State And Persistence
Each instance stores derived numeric mapping parameters. No persistence.

## Dependencies And Integration
Depends on NumPy and Python `math`. Used by `ddsketch_conversion.py` and `export_graph.py` to interpret DDSketch JSON buckets.

## Risks
Invalid `errorGuarantee` values near or above 1 can divide by zero or produce invalid gamma. Non-positive samples are not guarded before `np.frexp`. `reverseLog()` can encounter invalid square-root/cube-root domains from unexpected indices. Class attributes are shadowed by instance assignments, which is fine but can confuse readers.

## Test Signals
Round-trip sample-to-bucket-to-value tests across small and large values, invalid error guarantees, monotonicity of indexes, and comparison against a reference DDSketch implementation.
