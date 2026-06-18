# sources/storage-engines/pebble/compaction_delete_test.go

## Purpose
`compaction_delete_test.go` defines datadriven coverage for delete-only compaction hints and execution. It constructs in-memory Pebble DB states, forces table-stat collection to populate wide tombstone hints, triggers scheduling, inspects hint state, inspects compaction event summaries, verifies LSM layout changes, and exercises interactions with snapshots, flushes, batches, ingests, and manual compactions.

## Important APIs, Types, And Functions
The single test is `TestCompactionDeleteOnlyHints`. It uses `datadriven.RunTest` with commands `reset`, `define`, `batch`, `flush`, `get-hints`, `maybe-compact`, `compact`, `close-snapshot`, `iter`, `snapshot`, `ingest`, and `describe-lsm`.

The `reset` helper closes any previous DB and snapshots, creates an in-memory `vfs.NewMem` filesystem, enables newest format, enables delete-only excises, sets `DebugCheckLevels`, disables table stats by default for deterministic scheduling, configures single compaction concurrency, and installs an event listener that records `CompactionEnd`.

The `compactionString` helper waits for active compaction goroutines through `d.mu.compact.cond`, normalizes job IDs, durations, and file numbers, sorts compaction summary strings, clears the capture buffer, and returns deterministic text for datadriven comparison.

## Control Flow
Each datadriven command mutates or inspects the shared DB. `define` builds a DB from textual state and returns the current version string. `batch`, `flush`, `compact`, `ingest`, and `iter` delegate to existing test helpers. `snapshot` leaks the snapshot intentionally within the test scope so later `close-snapshot` can locate it by sequence number and test whether closing it unblocks delete-only compaction.

`get-hints` temporarily enables table stats and disables automatic compactions while forcing `collectTableStats` or waiting for an existing stats job. This isolates hint collection from actual compaction scheduling. It then returns `d.mu.compact.wideTombstones.String()`.

`maybe-compact` calls `d.maybeScheduleCompaction()` under `DB.mu`, prints the remaining wide tombstone hints, then prints normalized compaction summaries after waiting for launched jobs. `close-snapshot` closes a selected snapshot and returns any compaction summaries triggered by that closure. `describe-lsm` normalizes nondeterministic file numbers with a regexp.

## State And Persistence Behavior
Test state is entirely in-memory through `vfs.NewMem`, but it exercises the same manifest/version state as production Pebble. Captured `CompactionInfo` records are normalized before comparison. `compactInfo` is reset after each summary-producing command to keep datadriven outputs local to the command.

The test deliberately toggles `DisableTableStats` and `DisableAutomaticCompactions` around stats collection, because table stats are both the source of wide tombstone hints and a potential trigger for background compactions. It also closes all snapshots before DB reset/close to avoid leaking protected sequence numbers across test cases.

## Dependencies And Integration Points
The test integrates with Pebble's datadriven test infrastructure, DB definition/build/ingest/compact helper commands, leak detection, the in-memory VFS, event listeners, snapshot list internals, table stats collection, wide tombstone hint state, and compaction scheduling. It is the direct test signal for the production code in `compaction_delete.go` and for the wide-tombstone hint data maintained elsewhere.

## Risks
The test reaches into DB internals under `d.mu`, including snapshot lists, version strings, compact condition variables, and wide tombstone state. That gives strong coverage but makes the test sensitive to internal formatting, event summary text, and scheduling order. It mitigates nondeterminism by forcing single compaction concurrency, sorting compaction summaries, and replacing file numbers.

The helper intentionally lets snapshots remain unclosed until a later command, so any command sequence that forgets cleanup relies on the deferred `closeAllSnapshots`. The `get-hints` command unlocks around `collectTableStats` to avoid deadlock, which mirrors production lock concerns but requires careful relocking.

## Test Signals
Passing this datadriven test indicates that wide tombstone hints are collected deterministically from table stats, that delete-only compactions remove or excise the expected files, that snapshots delay deletion until safe, that compaction events are emitted with reason `delete-only` and excise annotations when appropriate, and that the LSM remains valid under debug level checks after flush, ingest, compact, and iterator verification commands.
