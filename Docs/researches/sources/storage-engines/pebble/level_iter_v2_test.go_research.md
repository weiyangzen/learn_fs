# sources/storage-engines/pebble/level_iter_v2_test.go

Purpose: this datadriven test exercises `levelIterV2` with fake per-file iterators, focusing on `TrySeekUsingNext`, prefix seeking, explicit spans, synthetic file boundaries, and bounds handling without the overhead of real SSTables.

Important APIs/types/functions: `TestLevelIterV2` defines an internal `file` struct with point keys, range-deletion spans, and bounds. Its `newIters` callback returns `base.NewFakeIter` for points and `keyspan.NewIter` for spans according to requested `iterKinds`. The datadriven `define` command builds files and manifest metadata; the `iter` command creates `newLevelIterV2` and delegates operation execution to `iterv2.RunIterOps`.

Control flow: input is grouped by `F` markers. Lines containing `:{` are parsed as keyspan spans; other fields are parsed as internal point keys. Metadata extends point bounds with both point keys and range-delete sentinel keys, then initializes physical backing. Each `iter` command optionally applies lower/upper bounds, sorts metadata into a `LevelSlice`, constructs the v2 iterator, and runs scripted operations such as first, next, seek-ge, and seek-prefix-ge.

State and persistence behavior: state is test-local slices of fake files and metadata. The fake iterators enforce per-table bounds but do not touch storage. Iterators are closed after each command.

Dependencies and integration points: depends on `datadriven`, `crstrings`, `iterv2.RunIterOps`, fake internal iterators, manifest metadata, test comparers, and keyspan parsing. It complements the randomized SSTable-backed test by allowing concise, deterministic coverage of edge cases.

Risks and test signals: because fake iterators may not reproduce every SSTable property, this test is best for control-flow semantics rather than block/filter behavior. It provides strong signals for boundary emission, prefix mode, `TrySeekUsingNext` state transitions, and correct metadata construction from spans.
