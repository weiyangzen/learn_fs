# sources/storage-engines/pebble/internal/datatest/datatest.go

## Purpose
This file provides reusable datadriven test helpers outside the root Pebble package, including batch definition parsing, compaction tracking, SST building, and ingest-and-excise command execution.

## Important APIs, Types, And Functions
`DefineBatch` parses operations into a `pebble.Batch`. `CompactionTracker`, `NewCompactionTracker`, and `WaitForInflightCompactionsToEqual` track compaction begin/end events. `RunBuildSSTCmd`, `WithDefaultWriterOpts`, and internal option helpers build SST files. `RunIngestAndExciseCmd` parses datadriven args and calls `DB.IngestAndExcise`.

## Control Flow
`DefineBatch` walks each input line, validates argument counts, converts `<nil>` keys to empty strings, and calls batch mutation APIs. `NewCompactionTracker` attaches event listeners that increment/decrement a condition-protected count. SST building parses writer options, creates a file, writes parsed test SST data, closes writer, and returns metadata. Ingest/excise collects `.sst` args and an optional `excise=start-end` span.

## State And Persistence Behavior
Batch helpers mutate caller-provided batches. SST building writes to the provided VFS path. Compaction tracking is in-memory listener state. Ingest/excise mutates the provided DB.

## Dependencies And Integration Points
It integrates with public Pebble APIs, `datadriven`, `sstable`, `objstorageprovider`, `vfs`, and event listeners.

## Risks And Edge Cases
The helpers are test-only but can trigger real DB mutations. Argument validation must stay aligned with public API semantics. `WaitForInflightCompactionsToEqual` requires listener attachment and can block indefinitely if expected events do not arrive.

## Test Signals
No direct tests are listed here; downstream datadriven tests using these helpers provide coverage through successful command execution and expected DB state.
