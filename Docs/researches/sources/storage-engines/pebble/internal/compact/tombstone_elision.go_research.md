# sources/storage-engines/pebble/internal/compact/tombstone_elision.go

## Purpose
This file computes and applies policies for eliding point tombstones, range deletion tombstones, and range-key unset/delete markers during compaction.

## Important APIs, Types, And Functions
`TombstoneElision` stores a mode and ordered in-use key ranges. Constructors are `NoTombstoneElision` and `ElideTombstonesOutsideOf`; methods include `ElidesNothing`, `ElidesEverything`, and `String`. `pointTombstoneElider` and `rangeTombstoneElider` implement ordered `ShouldElide` checks. `SetupTombstoneElision` derives policies from a manifest version, L0 organizer, output level, and compaction bounds.

## Control Flow
Eliders advance an index over sorted in-use ranges as keys/ranges are queried in order. A point tombstone can be elided if no in-use range contains the key. A range tombstone can be elided if it does not overlap any in-use range. Setup calculates lower-level in-use ranges, optimizes the fully-covered case to no elision, and currently applies the same policy to point and range-key tombstones.

## State And Persistence Behavior
Elision state is transient but affects durable compaction output by dropping tombstones that cannot shadow lower-level data. Eliders mutate their in-use index and require ordered calls.

## Dependencies And Integration Points
It depends on `base.UserKeyBounds`, `manifest.Version.CalculateInuseKeyRanges`, and `manifest.L0Organizer`. It feeds `Iter`, `RangeDelSpanCompactor`, and `RangeKeySpanCompactor`.

## Risks And Edge Cases
Incorrect elision can resurrect deleted data or retain unnecessary tombstones. Ordered-call assumptions are enforced only under invariants. L0 needs special handling because L0 files overlap. A TODO notes that point-key and range-key in-use ranges should eventually be calculated separately.

## Test Signals
`tombstone_elision_test.go` checks raw eliders, setup-derived in-use ranges, and integration-style point/range elision decisions from manifest versions.
