# sources/storage-engines/rocksdb/util/ribbon_config.h

## Purpose
Declares the Ribbon configuration API for estimating addable entries from slots and slots from entries under bounded construction failure probabilities.

## Important APIs, Types, And Functions
`ConstructionFailureChance` enumerates `kOneIn2`, `kOneIn20`, and `kOneIn1000`. `BandingConfigHelper1<kCfc, kCoeffBits, kUseSmash, kHomogeneous>` exposes compile-time failure-chance helpers. `BandingConfigHelper1TS` derives parameters from `TypesAndSettings`. `BandingConfigHelper<TypesAndSettings>` offers runtime selection of failure chance and defaults to `kOneIn1000` for homogeneous filters or `kOneIn20` otherwise.

## Control Flow
The runtime helper switches on `ConstructionFailureChance` and dispatches to the corresponding template instantiation. Unsupported settings inherit an assert-only implementation that returns zero.

## State And Persistence
No mutable state. The API is a pure configuration calculation interface backed by implementation tables in `ribbon_config.cc`.

## Dependencies And Integration Points
Depends on RocksDB namespace, `port/lang.h` for fallthrough annotations, and standard math/array headers. It integrates with `ribbon_impl.h` consumers selecting filter sizes before building `StandardBanding` and solution storage.

## Risks
Only 64- and 128-bit coefficient rows are supported by the data-backed implementation. Callers must still round slots for the chosen solution layout, especially interleaved layout. Failure chance is per seed; total construction failure after reseeding depends on seed count. Homogeneous filters should not use failure chance looser than the target false-positive rate.

## Test Signals
Ribbon tests consume this API across many settings and compare empirical reseed rates and false-positive rates. The `FindOccupancy` test/tool is the source of the data used by the implementation.
