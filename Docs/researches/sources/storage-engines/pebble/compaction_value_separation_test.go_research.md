# sources/storage-engines/pebble/compaction_value_separation_test.go

Purpose: Unit-tests `shouldWriteBlobFiles`, the central policy decision for value separation during compaction.

Important APIs/types/functions: `makeTestTableMeta` constructs table metadata with point bounds, physical backing, blob reference depth, and value-separation sstable properties. `TestShouldWriteBlobFiles` defines case inputs and expected write/preserve behavior.

Control flow: The test sets a default enabled policy, builds synthetic `compactionLevel` inputs, optionally overrides span policy behavior, calls `shouldWriteBlobFiles`, and asserts the write flag, reference depth, and `tableCompaction.annotations`.

State and persistence: Entirely in memory. State is limited to synthetic table metadata, backing properties, and the annotations slice on a `tableCompaction`.

Dependencies and integration: Uses `internal/base`, `manifest`, `sstable.Properties`, and `testify/require`. It directly targets production policy logic without invoking DB compaction execution or actual blob writing.

Risks: Does not cover L0 sublevel reference-depth summation, missing blob metadata, short attribute extraction, or full `determineCompactionValueSeparation` writer construction. Annotation string/order assertions are intentionally strict.

Test signals: Precise coverage for flush, virtual rewrite, preserve under low depth, rewrite when all inputs are pre-valsep, mixed pre/post preservation, max-depth rewrite, min-size mismatch, suffix mismatch, span policy split, and all-matching preservation.
