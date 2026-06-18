# sources/storage-engines/pebble/internal/manifest/table_metadata.go

## Purpose
`table_metadata.go` defines the central metadata object for tables in Pebble versions. It separates logical physical/virtual SSTable metadata from backing file metadata, tracks bounds, sequence numbers, blob references, compaction state, statistics, and formatting/parsing/validation helpers.

## Important APIs, Types, And Functions
- `TableMetadata` stores table identity, size, sequence bounds, point/range bounds, blob references, virtual table parameters, synthetic transforms, compaction state, stats, and reference counts.
- `TableBacking` represents the physical backing file shared by a physical SSTable or one or more virtual SSTables.
- `TableBackingProperties`, `TableStats`, `TableInfo`, `RangeKeyKinds`, and `CompactionState` expose supporting metadata.
- Key methods include `Ref`, `Unref`, `InitPhysicalBacking`, `InitVirtualBacking`, `AttachVirtualBacking`, `ValidateVirtual`, `SetCompactionState`, `ExtendPointKeyBounds`, `ExtendRangeKeyBounds`, `Validate`, `DebugString`, and `ParseTableMetadataDebug`.
- Bound helpers include `Smallest`, `Largest`, `UserKeyBounds`, `UserKeyBoundsByType`, `ContainsKeyType`, `SmallestBound`, `LargestBound`, and `boundsMarker`.

## Control Flow
Bounds are extended through dedicated methods so point bounds, range bounds, combined overall bounds, `HasPointKeys`, `HasRangeKeys`, and `RangeKeyKinds` stay consistent. Refcount methods cascade from table references to backing references and report obsolete backings when counts reach zero. Virtual backing attachment builds `virtual.VirtualReaderParams` from final bounds. Validation checks bounds, key kinds, sequence ranges, backing presence, blob reference depth, and synthetic prefix/suffix invariants.

## State And Persistence Behavior
Most fields are reconstructed from MANIFEST version edits. `CompactionState`, `AllowedSeeks`, stats population flags, reference counts, and `LargestSeqNumAbsolute` restart behavior are in-memory concerns. Blob reference estimates are stable over a table lifetime because level aggregate sizes depend on them. Physical backing references determine when table files become obsolete.

## Dependencies And Integration Points
The file depends on `base`, `sstable`, `sstable/block`, `sstable/virtual`, invariant utilities, structured parsing, redaction, and blob metadata types. It is used by every manifest version, level, version edit, compaction, event, and object lookup path.

## Risks And Test Signals
Risks are high because this struct sits on most manifest paths. Particular hazards include virtual table backing invariants, range-key-only bounds, manifest backward compatibility, blob reference depth/value-size semantics, refcount underflow, and struct-size growth. `table_metadata_test.go` covers bound extension, debug parse roundtrips, statistic scaling, and expected struct sizes; version edit tests cover persisted encoding.
