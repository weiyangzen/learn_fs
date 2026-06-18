# sources/storage-engines/pebble/internal/tombspan/tombspan_test.go

## Purpose
This file provides datadriven tests for wide tombstone tracking and delete-only compaction picking.

## Important APIs, Types, and Functions
`TestSet` runs `testdata/set`; `TestPartialPromotion` runs `testdata/partial_promotion`. `runSetTest` maintains table metadata, a `tombspan.Set`, and parsed manifest versions. `parseWideTombstone` parses lines such as `L1.1 [a,b) seqnums{point=[1-2], range=[3-4]}` using `strparse`. Datadriven commands include `define-version`, `add`, `update-with-earliest-snapshot`, `pick-compaction`, and `mark-as-compacting`.

## Control Flow and State
Versions are parsed from debug strings and table pointers are indexed by disk file number. Added tombstones reference those table objects. Snapshot update and compaction-pick commands mutate the shared set. Marking a table compacting mutates table metadata so subsequent picks can exercise skip/preserve behavior.

## Dependencies and Integration
The test depends on `datadriven`, `manifest.ParseVersionDebug`, `strparse`, `testkeys.Comparer`, and Pebble base types. It tests integration between tombstone tracking and manifest version metadata rather than only isolated helpers.

## Risks and Gaps
The parser is tailored to fixture syntax and may panic/fail on small format deviations. The tests are scenario-based and do not fuzz arbitrary overlapping tombstone regions or concurrent picker interactions.

## Test Signals
The fixtures are the strongest executable documentation for when a tombstone remains pending, when it promotes, and whether a table is deleted, excised, skipped, or forgotten.
