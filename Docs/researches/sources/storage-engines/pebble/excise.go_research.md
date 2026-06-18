# sources/storage-engines/pebble/excise.go

## Purpose
Implements `DB.Excise`, which atomically removes all data overlapping a key span, including data visible to snapshots, by applying an ingest/excise operation and splitting affected SSTables into virtual remnants.

## Important APIs, Types, And Functions
`DB.Excise` validates read/write state, unsuffixed bounds, and `FormatVirtualSSTables`. `exciseBoundsPolicy` selects tight, loose, or local-only tight bounds. `exciseTable` creates left/right virtual `TableMetadata` around the excised span. Helpers include `exciseOverlapBounds`, loose/tight bound calculators, `determineExcisedTableSize`, `determineExcisedTableBlobReferences`, and `applyExciseToVersionEdit`.

## Control Flow
The public method delegates to `d.ingest` with an excise span. For each overlapping table, `exciseTable` first drops tables fully contained in the span. Partial overlaps create virtual left and/or right tables. Tight mode opens point, range deletion, and range key iterators to find precise remaining bounds; loose mode uses sentinel bounds without reading remote data. Valid remnants attach the original backing, estimate size, copy scaled blob references, validate metadata, and are added to a version edit while the original is deleted.

## State And Persistence Behavior
Durable changes are manifest edits: delete original tables, optionally record created backing-table metadata, and add new virtual tables referencing existing backing files. Excise does not rewrite table contents in this file; it changes the LSM's metadata view. Blob references are conservatively copied and scaled to preserve value-separation accounting.

## Dependencies And Integration Points
Depends on ingest machinery, manifest metadata, virtual SSTable format, iterators from the file cache, object-storage locality checks, eventually file-only snapshots, range deletion/key iterators, and format-major-version gates. It interacts with download because excised external files may cancel or reshape download compactions.

## Risks And Edge Cases
Inclusive upper bounds require tight bounds and reject truncating point/range data at the inclusive end. Loose remote bounds may create broader virtual files and estimated sizes. Empty remnants must be discarded. EFOS protected ranges can extend overlap work. Size estimation can return zero, so the code forces size one to avoid later divide-by-zero behavior.

## Test Signals
Covered by `excise_test.go` datadriven excise, concurrent excise, and bounds tests. Signals include LSM debug output, iterator results, backing pointer confirmation, metrics, table stats, and dry-run version edits.
