# sources/storage-engines/pebble/sstable/internal.go

## Purpose
Re-exports internal key kinds and key/span aliases from public `sstable`, and asserts scratch-buffer sizing for value/blob handles.

## Important APIs, Types, and Functions
- Constants alias `base.InternalKeyKind*` values that are part of the file format.
- `InternalKey` aliases `base.InternalKey`.
- `Span` aliases `keyspan.Span`.
- Compile-time constants assert `blockHandleLikelyMaxLen` can hold value block index handles, value handles plus prefix byte, and blob inline handles plus prefix byte.

## Control Flow
No runtime flow. Compile-time arithmetic asserts buffer-size invariants.

## State and Persistence Behavior
No state is stored. The aliases expose file-format key kinds and key/span types to external SSTable users. Size assertions protect writer scratch buffers used when encoding handles into persisted values/metaindex entries.

## Dependencies and Integration Points
Depends on `base`, `keyspan`, `blob`, and `valblk`. Used by writers, tests, and external callers constructing SSTables.

## Risks and Edge Cases
Changing handle maximum lengths can break compile-time assertions and requires revisiting writer scratch buffer sizing. Key-kind aliases are file-format sensitive and must remain compatible with existing SSTables.

## Test Signals
Assertions are compile-time. Runtime behavior is covered indirectly by writer/value/blob tests.
