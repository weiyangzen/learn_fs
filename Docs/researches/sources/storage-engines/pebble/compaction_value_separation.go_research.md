# sources/storage-engines/pebble/compaction_value_separation.go

Purpose: Determines whether a compaction should never separate values, preserve existing hot blob references, or write values into new blob files.

Important APIs/types/functions: `neverSeparateValues`, `DB.determineCompactionValueSeparation`, `shouldWriteBlobFiles`, `compactionBlobReferenceDepth`, and `uniqueInputBlobMetadatas`.

Control flow: `determineCompactionValueSeparation` gates on format version and policy. It collects input blob metadata for non-flush compactions, calls `shouldWriteBlobFiles`, then returns either `valsep.NewPreserveAllHotBlobReferences` or `valsep.NewWriteNewBlobFiles`. The write path wires blob object creation, writer options, short attribute extraction, input blob files, and invalid-value event reporting.

State and persistence: May create new compaction blob files and update compaction bytes-written metrics. Preservation carries physical blob metadata forward. `shouldWriteBlobFiles` mutates `tableCompaction.annotations` with reason strings for rewrite decisions.

Dependencies and integration: Depends on `ValueSeparationPolicy`, `SpanPolicyFunc`, `manifest` blob metadata/reference depth, `objstorage`, `valsep`, sstable backing properties, comparer behavior, and the event listener API.

Risks: Policy matching is subtle around pre-valsep files, span policy coverage, suffix-disabling overrides, and reference-depth approximation. L0 depth sums sublevel maxima; other levels use per-level maxima. Missing blob metadata panics as an assertion failure.

Test signals: Unit tests cover flush, virtual rewrite, low/exceeded reference depth, pre/post-valsep mixes, policy mismatches, multiple span policies, and all-matching preservation.
