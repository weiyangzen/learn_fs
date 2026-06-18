# sources/storage-engines/pebble/compaction_picker_test.go

Purpose: This file is a broad test suite for Pebble's compaction picker. It verifies level sizing, base-level and target-level choice, L0 sublevel handling, in-progress compaction exclusion, compaction concurrency, read-triggered and tombstone-density compactions, selected input expansion, output file size limits, compensated size accounting, and score reporting.

Important APIs/types/functions: `loadVersion`, `parseTableMeta`, and `parseCompactionLines` build synthetic versions and in-progress compactions. Key tests include `TestCompactionPickerByScoreLevelMaxBytes`, `TestCompactionPickerTargetLevel`, `TestCompactionPickerL0`, `TestCompactionPickerConcurrency`, `TestCompactionPickerPickReadTriggered`, `TestPickedCompactionSetupInputs`, `TestPickedCompactionExpandInputs`, `TestCompactionOutputFileSize`, `TestCompactionPickerCompensatedSize`, `TestCompactionPickerPickFile`, and `TestCompactionPickerScores`. `alwaysMultiLevel` forces multi-level candidates; `pausableCleaner` controls cleaner timing.

Control flow: Most tests parse datadriven LSM descriptions, create `manifest.Version` plus `latestVersionState`, initialize `compactionPickerByScore`, and run commands like `queue`, `pick`, `pick-auto`, `pick_manual`, `mark-for-compaction`, and `scores`. Tests manually mark files compacting, update L0 organizer state, and reset state for deterministic repeated picks.

State and persistence: Synthetic state is held in versions, table metadata, compaction flags, L0 organizer state, marked-for-compaction sets, and optional problem spans. Some tests open a real in-memory DB to exercise stats, ingests, excises, and cleaner behavior.

Dependencies and integration: Integrates with `manifest`, `problemspans`, `sstable`, `datadriven`, `testkeys`, and helpers from `compaction_test.go` and `data_test.go`. It checks picker behavior expected by scheduler priority ordering.

Risks: The tests rely on exact string output, internal field access, and precise compacting-state manipulation. Missing L0 organizer updates or asynchronous table stats can cause misleading failures.

Test signals: Strong coverage for level score computation, target-level choice, L0 semantics, concurrency limits, read-triggered picking, multi-level heuristics, table boundary checks, deletion-compensated size, problem span avoidance, and score metrics.
