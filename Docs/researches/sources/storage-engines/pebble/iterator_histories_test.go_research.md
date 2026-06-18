# sources/storage-engines/pebble/iterator_histories_test.go

## Purpose
Defines `TestIterHistories`, a large datadriven test harness for reproducible iterator histories. It models sequences of database mutations, ingests, compactions, batches, snapshots, cloned iterators, combined point/range iteration, range-key-only iteration, and iterator commands, then compares stable textual output against files under `testdata/iter_histories`.

## Important APIs, Types, And Functions
`TestIterHistories` is the main entry point. It maintains a current `*DB`, named `*Iterator`s, named indexed `*Batch`es, DB options, probe maps, and a shared output buffer. `newIter` wraps `Reader.NewIter`, stores named iterators, and sets `forceEnableSeekOpt` to make history output deterministic. `parseOpts` configures in-memory storage, `testkeys.Comparer`, block-property collectors, disabled automatic compactions, and the V1 iterator stack. `cleanup` closes batches, iterators, snapshots, the DB, and any replacement cache.

The datadriven commands include `define`, `reopen`, `reset`, `populate`, `batch`, `compact`, `flush`, `disable-flushes`, `enable-flushes`, `get`, `build`, `ingest-existing`, `ingest`, `layout`, `lsm`, `metrics`, `mutate`, `clone`, `commit`, `combined-iter`, `rangekey-iter`, `scan-rangekeys`, `iter`, and `wait-table-stats`. `pluckStringCmdArg` is a small helper for optional string arguments.

Probe support is wired by replacing `d.newIters` in `addProbeInjectingNewIters`, attaching `itertest.Probe`s to point iterators and keyspan probes to range-deletion iterators for selected table numbers. `combined-iter` builds `IterOptions{KeyTypes: IterKeyTypePointsAndRanges}` and supports mask suffix/filter, bounds, reader selection, point-key block-property filters plus `SkipPoint`, snapshots, L6 filters, and probes.

## Control Flow
The test walks every file in `testdata/iter_histories`, skipping `no_invariants` cases when invariant builds would introduce nondeterminism. Each datadriven file starts or resets DB state, then feeds commands to the harness. Commands either mutate durable state, create named live objects, perform iterator operations through `runIterCmd`, or print structural state such as LSM layout and metrics.

Named iterators and batches persist across commands until explicitly closed or until cleanup. This lets test files express long histories such as: open iterator, mutate underlying indexed batch, call `SetOptions` or clone, then continue iteration. `clone` parses optional iterator options from command input and can request `CloneOptions.RefreshBatchView`.

The combined iterator path clears probe maps, parses options, selects a reader (`DB`, batch, or snapshot), constructs an iterator with points and ranges enabled, runs scripted iterator operations, and appends lower-level probe logs. Range-key-only paths exercise `IterKeyTypeRangesOnly` through either `runIterCmd` or a direct scan that prints bounds and range-key data.

## State And Persistence Behavior
The harness uses `vfs.NewMem` and disabled automatic compactions for deterministic state. It may reopen the same in-memory FS through options, build external sstables, ingest them, compact explicit ranges, pause flushes by mutating `d.mu.compact.flushing`, and inspect snapshots by sequence number.

Cleanup is important because tests intentionally keep iterators, batches, and snapshots alive across command boundaries. It closes all named objects, enumerates and closes open snapshots under `d.mu.snapshots`, closes the DB, and unreferences a replacement cache when command-line options installed one.

## Dependencies And Integration Points
The file integrates Pebble's datadriven test utilities, `itertest` parser/probes, `testkeys` comparer and block properties, keyspan probe helpers, run-command helpers from other Pebble tests, `manifest` table metadata, `sstable` test filters, in-memory VFS, and `require` assertions. It is explicitly V1-iterator-stack-specific pending a TODO to port to V2.

It directly exercises public `Reader` interfaces (`DB`, `Batch`, snapshots) and iterator internals needed for deterministic testing (`forceEnableSeekOpt`, `d.newIters` replacement, snapshot list inspection).

## Risks And Edge Cases
The harness has broad mutable shared state, so missing cleanup can leak references and influence later datadriven files. Replacing `d.newIters` is powerful but couples the test to DB internals. Because invariant builds may randomize iterator optimization/reconstruction behavior, the test disables those optimizations on created iterators and skips known nondeterministic files.

Batch mutation and clone histories are especially sensitive to iterator semantics around stale batch views, `SetOptions`, range deletion iterators, and range-key stacks. The point-key-filter command must keep `PointKeyFilters` and `SkipPoint` logically aligned or the test would compare different layers of filtering.

## Test Signals
Failures point to regressions in end-to-end iterator behavior rather than isolated helper logic. The histories can reveal changed key ordering, bounds behavior, range-key surfacing, masking/filtering, batch refresh semantics, clone visibility, probe-level seek/next behavior, LSM layout assumptions, or resource lifecycle. Probe output provides lower-level evidence when internal iterator calls differ while user-visible output remains close.
