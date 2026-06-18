# sources/storage-engines/rocksdb/util/ribbon_config.cc

## Purpose
Implements Ribbon configuration lookup tables and interpolation logic that translate between number of slots and number of addable entries for selected construction failure probabilities.

## Important APIs, Types, And Functions
`BandingConfigHelperData<kCfc, kCoeffBits, kUseSmash>` stores known addable-entry counts at powers-of-two slot sizes and factor formulas for larger sizes. Explicit specializations provide data for 64-bit and 128-bit coefficient rows, smash and non-smash variants, and failure chances `kOneIn2`, `kOneIn20`, and `kOneIn1000`. `GetNumToAdd` and `GetNumSlots` implement interpolation and inverse interpolation. The file explicitly instantiates supported combinations with homogeneous and non-homogeneous variants.

## Control Flow
`GetNumToAdd` computes `log2(num_slots)`, interpolates between known power-of-two table entries when within the table, or uses a large-value overhead factor formula. Homogeneous configurations subtract eight from addable count as an empirical correction. `GetNumSlots` reverses this by adjusting homogeneous counts, choosing nearby power-of-two anchors, interpolating required slots, and rounding up.

## State And Persistence
Static lookup tables are compile-time program data. There is no runtime mutable state or persistence.

## Dependencies And Integration Points
Depends on `ribbon_config.h`, `<array>`, and `<cmath>`. The values are consumed by filter construction planning to choose slot counts for a target construction success probability. The data is derived from `FindOccupancy` tooling in `ribbon_test.cc`.

## Risks
The tables are empirical and only supported for 64- and 128-bit coefficient rows. Unsupported instantiations assert if used. Interpolation is approximate and assumes the observed distribution remains valid. Homogeneous correction is explicitly empirical and "mostly affecting small filter configurations." Large `num_to_add` values are documented as needing headroom below uint32 overflow.

## Test Signals
`ribbon_test.cc` uses `BandingConfigHelper` in compactness and construction-success tests and includes `FindOccupancy` tooling that generated the table data. Tests check reseed counts against expected failure rates.
