<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/meta_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/meta_test.go

Purpose: main Go test entry point for Pebble metamorphic testing. It dispatches between generating/running a full suite, re-running one run directory, comparing existing runs, and optional reduction.

Important APIs/functions: package globals `runOnceFlags, runFlags = metaflags.InitAllFlags()`, tests `TestMeta`, `TestMetaTwoInstance`, `TestMetaCockroachKVs`, interface `option`, and `runTestMeta`. The three tests differ by additional options: default, multi-instance, or Cockroach key format.

Control flow and state: each test optionally installs leaktest. `runTestMeta` first handles `--compare`, rejecting run-only flags, optionally reducing, then calling `metamorphic.Compare`. Next it handles `--run-dir`, similarly rejecting run-only flags and calling `metamorphic.RunOnce`. Otherwise it rejects run-once-only flags, builds `RunOptions`, appends test-specific options, and calls `metamorphic.RunAndCompare`.

Persistence and integration: generated state is under the configured `_meta` directory, including ops, options, histories, and DB directories. It integrates with `metaflags`, `leaktest`, and the core `pebble/metamorphic` package. Risks include global flag initialization side effects, invalid flag combinations, long-running generated workloads, and reproducibility depending on seed plus commit. Test signal is broad system-level coverage rather than narrow unit assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/meta_test.go -->
