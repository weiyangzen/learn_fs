# sources/storage-engines/pebble/sstable/tablefilters/table_filters.go

## Purpose
Centralizes registration and name parsing for SSTable table filter families supported by Pebble.

## Important APIs, Types, And Functions
`Decoders` lists Bloom and binary fuse decoders. `PolicyFromName` resolves `"none"`, Bloom names, adaptive Bloom names, and binary fuse names to `base.TableFilterPolicy`.

## Control Flow
Callers parse a configured policy name by checking the no-filter sentinel first, then delegating to Bloom and binary fuse package parsers. Readers can use `Decoders` to recognize filter families present in SSTables.

## State And Persistence Behavior
No mutable state. The file defines process-level decoder registration and policy lookup behavior.

## Dependencies And Integration Points
Integrates `base`, `bloom`, and `binaryfuse` packages with higher-level options/config parsing.

## Risks And Edge Cases
Parsing order means Bloom gets first chance after `"none"`, then binary fuse. Unknown names return `(nil,false)` and must be handled by callers.

## Test Signals
Covered indirectly by Bloom adaptive name tests, binary fuse policy parsing, and any option parsing that calls `PolicyFromName`.
