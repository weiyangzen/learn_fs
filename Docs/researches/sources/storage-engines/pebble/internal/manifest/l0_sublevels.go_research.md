# sources/storage-engines/pebble/internal/manifest/l0_sublevels.go

## Purpose
This file implements Pebble's L0 sublevel organization and L0 compaction-selection machinery. It turns overlapping L0 files into non-overlapping sublevel slices, computes interval metadata for fast overlap reasoning, tracks in-progress compactions, chooses L0-to-base and intra-L0 compaction candidates, exposes flush split keys, and maintains the current organizer state across version edits.

## Important APIs, Types, And Functions
Key types include `intervalKey`, `l0FileState`, `fileInterval`, `L0Compaction`, `l0Sublevels`, `L0CompactionFiles`, `L0Organizer`, and `L0PreparedUpdate`. Construction and update functions include `newL0Sublevels`, `sortAndSweep`, `mergeIntervals`, `canUseAddL0Files`, `addL0Files`, and `addFileToSublevels`. Runtime APIs include `InitCompactingFileInfo`, `ReadAmplification`, `InUseKeyRanges`, `FlushSplitKeys`, `MaxDepthAfterOngoingCompactions`, `PickBaseCompaction`, `PickIntraL0Compaction`, `ExtendL0ForBaseCompactionTo`, `UpdateStateForStartedCompaction`, `NewL0Organizer`, `PrepareUpdate`, `PerformUpdate`, `SubLevelOf`, and `ResetForTesting`.

## Control Flow
`newL0Sublevels` builds interval boundary keys from every L0 file's smallest and largest user key, sorts/deduplicates them, assigns each file a min/max interval index, adds files in increasing L0 sequence order, sorts per-sublevel files by interval, builds `LevelSlice` B-trees, computes flush split keys, and runs invariant checks. `addL0Files` is an incremental fast path for pure additions at the top of L0: it shallow/deep copies the old state as needed, merges new interval keys into old intervals, remaps old file interval indexes, updates estimated bytes, inserts new files, rebuilds affected sublevel slices, and recomputes flush split keys.

## State, Persistence, And Side Effects
`l0Sublevels` is derived in-memory state for the current version. It stores immutable level slices plus mutable compaction counters/flags initialized under DB and manifest locks. Per-file state is indexed by L0 order and mapped by table number. Flush split keys are derived from interval byte estimates and `flushSplitBytes`. `L0Organizer` owns current L0 metadata, sublevels, and a generation counter; `PrepareUpdate` can run concurrently to precompute work, while `PerformUpdate` applies one prepared update and sets `newVersion.L0SublevelFiles`.

## Compaction Behavior
Base compaction picking scores intervals by stack depth minus compacting files, prioritizes intervals not near base-compacting ranges, skips problem spans, seeds from the lowest sublevel file in a hot interval, and grows a triangular candidate downward to preserve sequence correctness. It rejects candidates blocked by compacting Lbase files. Intra-L0 picking is used when base compaction cannot be chosen; it seeds from the highest eligible sublevel, excludes files newer than `earliestUnflushedSeqNum`, grows an inverted triangle, and may extend toward a rectangle when safe. Both paths cap candidate growth heuristically when bytes jump sharply beyond 100 MiB or exceed a 500 MiB hard threshold after a viable candidate exists.

## Dependencies And Integration Points
The file depends on `bytes`, `cmp`, `fmt`, maps/slices/sort/math/strings, CockroachDB errors, Pebble `base`, invariants, and `problemspans`. It integrates with `LevelMetadata`, `LevelSlice`, `TableMetadata` compaction flags, `Version.L0SublevelFiles`, `BulkVersionEdit`, compaction picker scheduling, flush splitting, problem-span avoidance, and the proof sketch in `doc.go`.

## Risks And Edge Cases
Inclusive largest-key handling is subtle because intervals simulate immediate successors with an `isInclusiveEndBound` flag. Incremental add remapping is complex and must update old file interval indexes, inherited interval contents, byte estimates, and affected B-trees exactly. Compaction state must be initialized under the right locks because `TableMetadata.Compacting` fields are not safe to read during sublevel construction. Candidate extension must avoid compacting files and avoid selecting files that would require unselected older/younger versions of the same keys. The `PickIntraL0Compaction` allocation currently creates a slice length equal to intervals even though skipped entries keep zero values, making zero-interval handling worth watching.

## Test Signals
This file is covered by L0 sublevel tests outside this subset, including sublevel construction, incremental add equivalence, and benchmarks noted by `rg`. In this subset, `doc.go` provides the design proof and `btree`/level metadata tests validate core structures used by `LevelSlice`. Runtime invariant checks (`Check`, `verifyLevelMetadataTransition`, occasional rebuild comparison in `PerformUpdate`) provide strong debug-mode signals.
