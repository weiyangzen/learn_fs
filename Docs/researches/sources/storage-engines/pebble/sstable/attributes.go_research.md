# sources/storage-engines/pebble/sstable/attributes.go

## Purpose
This file defines an `Attributes` bitset describing notable features present in an SSTable, such as value blocks, range keys, range deletions, two-level indexes, blob values, and point keys.

## Important APIs, Types, and Functions
`Attributes` is a `uint32` bitset. Constants include `AttributeValueBlocks`, `AttributeRangeKeySets`, `AttributeRangeKeyUnsets`, `AttributeRangeKeyDels`, `AttributeRangeDels`, `AttributeTwoLevelIndex`, `AttributeBlobValues`, and `AttributePointKeys`.

`Intersects` checks whether any requested bits are present. `Has` checks whether all requested bits are present. `Add` mutates the receiver by OR-ing bits. `String` returns a deterministic bracketed comma-separated list for testing and diagnostics.

## Control Flow
The methods are direct bit operations. `String` appends names in constant declaration order and joins them.

## State and Persistence Behavior
No persistence is performed here, but the bitset likely reflects persisted table properties or computed table metadata elsewhere in the sstable package.

## Dependencies and Integration Points
The only dependency is `strings`. Callers use attributes to reason about table contents and feature-dependent behavior.

## Risks
Adding new attributes requires updating `String` to keep diagnostics complete. `Has(0)` returns true by bitset convention, which callers should understand.

## Test Signals
No direct test file is listed, but string output is explicitly described as for testing and should be covered where attributes are emitted.
