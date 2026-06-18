# sources/storage-engines/pebble/internal/compact/tombstone_elision_test.go

## Purpose
This file tests tombstone elision primitives and setup logic derived from manifest versions.

## Important APIs, Types, And Functions
`TestTombstoneElider` tests point and range eliders from explicit policies. `TestSetupTombstoneElision` parses versions and prints policies for output levels and bounds. `TestTombstoneElision` combines setup with point/range `ShouldElide` decisions.

## Control Flow
Datadriven `init` commands choose either no elision or explicit in-use ranges. `points` and `ranges` print elide/don't-elide decisions. Version-based tests build an `L0Organizer` and manifest `Version`, call `SetupTombstoneElision`, then feed requested keys/ranges through eliders.

## State And Persistence Behavior
All state is in-memory manifest/test metadata. The behavior validated affects future persisted compaction outputs by deciding which tombstones disappear.

## Dependencies And Integration Points
The tests depend on `datadriven`, `manifest.ParseVersionDebug`, `manifest.NewL0Organizer`, `base.UserKeyBounds`, `testkeys`, and the elision APIs.

## Risks And Edge Cases
Tests cover empty in-use sets, overlapping/adjacent lower-level spans, L0 handling, point versus range queries, and ordered query behavior. They do not yet validate the TODO for separate point/range-key in-use range calculation.

## Test Signals
Exact datadriven text demonstrates whether tombstones are retained when lower-level data overlaps and elided when outside all in-use ranges.
