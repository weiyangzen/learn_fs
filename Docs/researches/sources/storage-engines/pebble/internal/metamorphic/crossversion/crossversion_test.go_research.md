<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go

Purpose: implements cross-version metamorphic testing by chaining `internal/metamorphic` test binaries from multiple Pebble SHAs. It exercises upgrade and migration paths by running an older version, retaining database states, and using those states as initial inputs to later versions.

Important APIs/types: flags `-seed`, `-factor`, repeated `-version`, `-artifacts`, and `-stream-output`; `TestMetaCrossVersion`, `runCrossVersion`, `runVersion`, `metamorphicTestRun.run`, `pebbleVersions.Set`, artifact helpers `dirsToSave`, `saveDirs`, and `fatalf`.

Control flow and state: a deterministic PRNG derives per-version seeds. For each version, the test runs all current initial states through a metamorphic test binary. It gathers every subrun directory and `history`, compares histories from same-version runs with different initial states, prunes retained states to `factor`, and carries those database directories plus prior `ops` paths forward. Failures clone artifacts once under a `sync.Once`.

Persistence and integration: state lives in temp directories with `_meta` subtrees, run histories, options, ops files, and optionally copied artifacts. It integrates with external compiled test binaries, `metamorphic.CompareHistories`, `vfs.Clone`, and shell scripts described by `reproductionCommand`. Risks include flaky subprocess timeouts, missing/mismatched binaries, high disk usage from retained DBs, path assumptions around `_meta`, and deterministic reproduction requiring the same commits. Test signal is this test itself; it is usually driven by CI scripts rather than ordinary unit runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/crossversion/crossversion_test.go -->
