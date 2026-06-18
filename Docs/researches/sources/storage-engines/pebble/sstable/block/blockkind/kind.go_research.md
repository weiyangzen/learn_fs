## sources/storage-engines/pebble/sstable/block/blockkind/kind.go

Purpose: Defines the low-cardinality enumeration of logical block kinds used for cache categories, compression accounting, read tracing, and per-kind metrics.

Important APIs/types/functions: `Kind` is a `uint8` enum. Values include `SSTableData`, `SSTableIndex`, `SSTableValue`, `BlobValue`, `BlobReferenceValueLivenessIndex`, `TieringHistogram`, `Filter`, `RangeDel`, `RangeKey`, and `Metadata`, plus `Unknown` and `NumKinds`. `String` maps enum values to stable short names. `All` yields kinds 1 through `NumKinds-1`.

Control flow: There is no complex control flow. `All` is an `iter.Seq` that stops early if the yield function returns false.

State and persistence behavior: The enum is not directly documented here as a durable on-disk value, but it is used throughout block read/write logic as a semantic category. Array indexes such as `[blockkind.NumKinds]` depend on numeric ordering and range stability within a process.

Dependencies and integration points: Imported by `block` as alias `Kind`, compression and category stats, cache category mapping, block writers, readers, and tracing. The string names appear in slow-read tracing and stats/debug surfaces.

Risks: `String` indexes `kindString[k]` without bounds checks beyond Go's slice panic; invalid kinds panic. Adding enum values requires updating `kindString`, `NumKinds`-sized arrays, cache category mappings, and any per-kind stat logic.

Test signals: No direct tests here in the subset. Indirect coverage comes from compressor tests using kind routing and reader/stat paths.
