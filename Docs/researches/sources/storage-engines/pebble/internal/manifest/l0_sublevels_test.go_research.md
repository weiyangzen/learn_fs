# sources/storage-engines/pebble/internal/manifest/l0_sublevels_test.go

## Purpose
This test file exercises Pebble manifest L0 sublevel construction, visualization, compaction selection, in-use range calculation, flush split keys, incremental L0 updates, and manifest replay benchmarks. It is the primary test signal for the L0 organizer behavior that turns unordered overlapping L0 files into ordered sublevels and compaction candidates.

## Important APIs, Types, And Helpers
- `readManifest` replays a record log manifest into a `Version` by repeatedly decoding `VersionEdit`, accumulating a `BulkVersionEdit`, applying it, and updating an `L0Organizer`.
- `visualizeSublevels` renders L0 sublevels and optional lower levels as compact ASCII spans, marking base compaction, intra-L0 compaction, and compacting states.
- `TestL0Sublevels` is datadriven and dispatches commands such as `define`, `add-l0-files`, `pick-base-compaction`, `pick-intra-l0-compaction`, `in-use-key-ranges`, `flush-split-keys`, `max-depth-after-ongoing-compactions`, `l0-check-ordering`, and `update-state-for-compaction`.
- `TestAddL0FilesEquivalence` randomized-checks incremental `addL0Files` against full `newL0Sublevels` reconstruction.
- Benchmarks cover manifest replay with L0 sublevels, fresh sublevel initialization, and initialization plus base compaction picking.

## Control Flow
The datadriven `define` path parses table specs into `TableMetadata`, sorts L0 by sequence number and L1+ by smallest key, constructs `LevelMetadata`, and either initializes sublevels from scratch or updates an existing sublevel structure with newly added L0 files. Compaction commands use the already-built `l0Sublevels` state to select compactions and then render the selection. State mutation commands mark files compacting and update L0 file state so subsequent queries observe active compactions.

## State And Persistence Behavior
The test reads actual MANIFEST testdata through Pebble record readers, so it covers persisted `VersionEdit` replay into in-memory `Version` and `L0Organizer` state. The datadriven parser constructs in-memory table metadata directly and initializes physical backings because later version/sublevel code expects backing state to exist.

## Dependencies And Integration Points
It integrates with `record.Reader`, `VersionEdit`, `BulkVersionEdit`, `Version`, `L0Organizer`, `LevelMetadata`, table compaction state, `base.Comparer`, and `datadriven`. Testdata under `internal/manifest/testdata/l0_sublevels` and `MANIFEST_import` is part of the effective contract.

## Risks And Test Signals
The riskiest areas are L0 ordering with overlapping user keys, incremental sublevel updates that depend on previous indices, active compaction state, and flush split key generation. The randomized equivalence test is a strong regression signal for `addL0Files`, while the benchmarks signal performance risk in manifest replay and L0 compaction selection.
