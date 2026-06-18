# sources/storage-engines/pebble/level_checker_test.go

Purpose: this test file validates the `CheckLevels` corruption checker across normal fixture databases, synthetic LSM layouts that intentionally violate invariants, merge-operator error paths, and blob liveness block validation.

Important APIs/types/functions: `TestCheckLevelsBasics` opens staged fixture DBs and asserts `DB.CheckLevels(nil)` succeeds. `failMerger` is a test `ValueMerger` that can fail during `MergeOlder` or `Finish` while tracking close balance. `TestCheckLevelsCornerCases` builds raw SSTables in an in-memory filesystem and feeds them through `checkLevelsInternal` with a custom `newIters`. `TestPerformValidationForSSTableFailures` constructs encoded blob-reference liveness blocks and verifies `performValidationForSSTable` rejects specific mismatches.

Control flow: the corner-case datadriven test parses `define` commands into logical levels, table metadata, raw SSTable contents, and optional writer modes like unfragmented range tombstones or disabled key-order checks. The `check` command wraps those files in a test `manifest.Version`, installs the requested merger, and runs `checkLevelsInternal`. The blob tests create a small reference-liveness block and compare decoder output against hand-built `referenced` maps for row-count, dangling-reference, bitmap, size, missing-reference, and success cases.

State and persistence behavior: all table files live in `vfs.NewMem`; readers are retained in a slice indexed by table number and closed by defer. The test intentionally constructs states production code would usually prevent, so it skips under invariants. It does not persist data beyond the test process.

Dependencies and integration points: exercises `sstable.RawWriter`, manifest metadata construction, object storage wrappers, range tombstone fragmentation, test key comparer formatting, invalidating iterators, blob liveness encoders/decoders, and the production `checkConfig` path. The custom iterator factory mimics table-cache behavior enough to test the checker without opening a full `DB`.

Risks and test signals: the tests are strong at negative-path validation because they can synthesize bad ordering, bad tombstone fragmentation, and merge failures. They depend on exact error-message substrings and table-number formatting, so diagnostic text changes can require fixture updates. They also deliberately bypass invariant checks; running with invariants enabled skips the corner cases.
