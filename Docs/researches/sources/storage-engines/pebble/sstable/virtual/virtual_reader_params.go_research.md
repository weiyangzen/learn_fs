# sources/storage-engines/pebble/sstable/virtual/virtual_reader_params.go

## Purpose
Defines the bounds and file number metadata needed to read a virtual SSTable and constrains requested spans to virtual bounds.

## Important APIs, Types, And Functions
`VirtualReaderParams` contains `Lower`, `Upper`, and `FileNum`. `ConstrainBounds(start, end, endInclusive, compare)` returns whether the last key is inclusive plus constrained first/last user keys.

## Control Flow
The method raises the start bound to the virtual lower bound if needed. It initializes the last bound from the virtual upper key and inclusivity from the upper sentinel kind, then narrows it with the caller end bound when the caller end is inside or equal to the virtual upper bound.

## State And Persistence Behavior
The struct carries manifest/reader metadata for virtual table views. The method is pure and does not persist state.

## Dependencies And Integration Points
Depends on `base.InternalKey`, file numbers, and comparer functions. Used by virtual SSTable reader paths to map physical table bounds to virtual spans.

## Risks And Edge Cases
The TODO notes undefined behavior if caller bounds are completely outside virtual bounds. Inclusivity handling depends on `Upper.IsExclusiveSentinel`.

## Test Signals
No direct tests in this file; coverage is expected through virtual SSTable reader behavior.
