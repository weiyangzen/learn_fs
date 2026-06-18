# sources/storage-engines/pebble/compaction_picker.go

## Purpose
`compaction_picker.go` chooses which compaction Pebble should run next. It computes LSM shape targets, scores levels, accounts for in-progress compactions, picks L0/base/intra-L0 work, chooses positive-level seed files, expands compaction inputs safely, optionally upgrades single-level compactions to multi-level compactions, and selects lower-priority maintenance work such as elision-only, tombstone-density, virtual-SST rewrite, blob-file rewrite, read-triggered, marked-for-rewrite, manual, and download compactions.

## Important APIs, Types, And Functions
`compactionEnv` is the picker input snapshot: disk availability, earliest unflushed/snapshot sequence numbers, in-progress compaction summaries, read-compaction queue state, and problem spans. `compactionPicker` defines the picker interface used by the version set. `pickedCompaction` is the scheduler-facing abstraction that can report manual ID, construct a concrete compaction, and describe scheduler priority.

`pickedTableCompaction` is the main picked result. It holds kind, score, manual ID, start/output levels, inputs, base level, L0 compaction files, bounds, version, L0 organizer, and picker metrics. It is constructed by `newPickedTableCompaction`, `newPickedCompactionFromL0`, `newPickedManualCompaction`, `pickDownloadCompaction`, `pickAutoLPositive`, `pickL0`, and `pickedCompactionFromCandidateFile`.

`compactionPickerByScore` owns the current version, mutable latest-version state, base level, per-level max-byte targets, and DB size. Important methods include `initLevelMaxBytes`, `getMetrics`, `getBaseLevel`, `estimatedCompactionDebt`, `calculateLevelScores`, `getCompactionConcurrency`, `pickHighPrioritySpaceCompaction`, `pickAutoScore`, `pickAutoNonScore`, `pickElisionOnlyCompaction`, `pickRewriteCompaction`, `pickVirtualRewriteCompaction`, `pickBlobFileRewriteCompactionHighPriority`, `pickBlobFileRewriteCompactionLowPriority`, `pickTombstoneDensityCompaction`, `pickReadTriggeredCompaction`, and `forceBaseLevel1`.

Input expansion and conflict helpers include `setupInputs`, `maybeGrow`, `maybeGrowL0ForBase`, `setupMultiLevelCandidate`, `canCompactTables`, `outputKeyRangeAlreadyCompacting`, `conflictsWithInProgress`, and `areUserKeysOverlapping`. Scoring helpers include `calculateLevelSizes`, `calculateSizeAdjust`, `calculateL0FillFactor`, `pickCompactionSeedFile`, `tableCompensatedSize`, `tableTombstoneCompensation`, `totalCompensatedSize`, and `responsibleForGarbageBytes`. Multi-level policy is abstracted through `MultiLevelHeuristic`, `NoMultiLevel`, and `WriteAmpHeuristic`.

## Control Flow
A new `compactionPickerByScore` is created for the latest version under the version-set log lock. `initLevelMaxBytes` computes the first non-empty level, total DB size, base level, and per-level max sizes, taking in-progress L0 output into account. `calculateLevelScores` then computes L0 fill factor from L0 sublevel depth and file count, computes L1+ fill factors from compensated sizes and in-progress adjustments, divides by next-level fill factor to prioritize lower levels, applies compensated thresholds, and returns candidates sorted by descending score.

`pickAutoScore` iterates scored candidates. For L0 it calls `pickL0`, which first asks `L0Organizer.PickBaseCompaction` for L0-to-base work using base-level files and problem spans, then falls back to `PickIntraL0Compaction` if a base compaction cannot be chosen. For L1+ it selects a seed file with `pickCompactionSeedFile`, builds a compaction with `pickAutoLPositive`, and optionally calls `maybeAddLevel` for multi-level expansion.

`setupInputs` is the central safety step. It rejects already compacting files and problem-span overlaps, extends bounds from input files, finds overlapping output-level files, rejects compacting/problem output files, optionally expands inputs without increasing output overlap, generates L0 sublevel info for L0 inputs, and rejects output key ranges already being written by another in-progress compaction. Multi-level setup appends the next level and reruns `setupInputs` for the intermediate-to-new-output pair.

Seed selection for positive levels scans start-level files and output-level overlap in order. It skips compacting/problem files, computes overlapping output bytes, subtracts bottommost range-deletion estimates when snapshots permit, and picks the lowest scaled overlap ratio using a compensated input size that includes file size, estimated tombstone benefit, estimated external reference size, and virtual-backing garbage responsibility.

If no score-based work is found, `pickAutoNonScore` tries maintenance compactions in priority order: tombstone-density compactions, bottommost elision-only compactions, virtual SST rewrites, low-priority blob-file rewrites, read-triggered compactions, and marked-for-compaction rewrites. It also toggles read-compaction rescheduling when no read compaction is selected.

Manual compaction picking computes the appropriate output level, detects conflicts with in-progress compactions so the manual request can retry rather than disappear, uses overlaps in the requested range as inputs, ignores problem spans, and may use multi-level expansion. Download compactions rewrite or copy one file in place and ignore problem spans while preserving conflict checks through `setupInputs`.

## State And Persistence Behavior
The picker itself persists no manifest changes. Its outputs are in-memory `pickedCompaction` objects consumed by `compaction.go`. It does, however, derive decisions from persisted manifest state: level slices, table metadata stats/properties, marked-for-compaction flags, virtual backing usage, blob file stats, L0 organizer state, and sequence-number bounds.

In-progress compaction state affects scoring and selection. `calculateSizeAdjust` models outgoing and incoming bytes unless the in-progress compaction's version edit is already applied. `calculateL0FillFactor` subtracts in-progress L0 inputs from the file-count score. `outputKeyRangeAlreadyCompacting` prevents two compactions from writing overlapping key ranges to the same output level even if their input files do not overlap. `getCompactionConcurrency` derives allowed concurrency from configured lower/upper bounds, L0 read amplification, estimated compaction debt, and compactable garbage fraction.

Picked compactions carry metrics such as level scores and overlapping ratios into `tableCompaction.makeInfo`, making picker decisions visible through compaction events. They also preserve L0 sublevel information needed later by iterator construction.

## Dependencies And Integration Points
This file is tightly coupled to `manifest.Version`, `manifest.LevelSlice`, `manifest.L0Organizer`, table metadata annotations, virtual backings, blob file metadata, deletion-byte annotators, and problem spans. It integrates with `Options` for level sizing, compaction concurrency, L0 thresholds, tombstone-density thresholds, virtual-SST rewrite thresholds, value-separation policy, deprecated scoring behavior, and multi-level heuristics.

The scheduler-facing integration is through `WaitingCompaction` and `scheduledCompactionMap`, while execution integration is through `pickedTableCompaction.ConstructCompaction`, which calls `newCompaction` in `compaction.go`. Manual compactions use `manualCompaction` state from `compaction.go`; read-triggered compactions use `readCompactionQueue`; blob-file rewrite picking returns `pickedBlobFileCompaction` defined elsewhere.

## Risks
Picker correctness depends on choosing inputs that preserve LSM invariants and avoid concurrent output overlap. The L0 path is especially subtle because L0 files may overlap and are organized by sublevels; missing L0 sublevel expansion or base-level conflict information can reduce concurrency or produce overlapping outputs.

Scoring and compensation are heuristic. Tombstone estimates, virtual-backing garbage responsibility, external reference sizes, and next-level fill-factor division can over- or under-prioritize space reclamation. Several thresholds are intentionally approximate, such as the L0 score formula, tombstone-density overlap cap, and high/low-priority blob garbage ratios.

The picker runs while holding important locks, so algorithms that scan levels or annotations must remain bounded. `pickCompactionSeedFile` is linear in start and output levels; multi-level picking clones compactions and reruns setup; comments explicitly call out the need to keep this path fast.

Manual and read-triggered compactions must not silently disappear. Manual conflicts return `retryLater`; read-triggered compactions verify the target file is still present and cap output overlap width. Errors in these guards could lead to surprising no-ops or excessive write amplification.

## Test Signals
Strong tests should cover base-level calculation, per-level score ordering, L0 file-count and sublevel-depth scoring, in-progress size adjustment, problem-span exclusion, output key-range conflict detection, L0-to-base and intra-L0 picking, positive-level seed selection, multi-level heuristic choices, manual retry semantics, read-triggered width limits, elision-only snapshot gating, tombstone-density thresholds, virtual-SST rewrite thresholds, blob-file rewrite priority thresholds, and marked-for-compaction rewrites.

Useful integration signals include compaction event metrics showing selected scores and overlapping ratios, scheduler waiting priorities for each compaction kind, invariant checks that picked inputs are ordered and non-overlapping where required, and randomized/metamorphic tests that run concurrent flush, ingest, manual compaction, excise, and automatic compaction scheduling.
