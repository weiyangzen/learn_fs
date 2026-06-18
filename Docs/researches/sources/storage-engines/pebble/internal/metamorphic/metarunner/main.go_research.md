<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go -->
# sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go

Purpose: small command-line runner for executing `metamorphic.RunOnce` or `metamorphic.Compare` outside `go test`, primarily for coverage instrumentation while maintaining flag compatibility with `TestMeta`.

Important APIs/types: package global `runOnceFlags = metaflags.InitRunOnceFlags()`, ignored `-test.run` flag, `main`, and `mockT` implementing `metamorphic.TestingT`.

Control flow and state: `main` parses flags, builds run-once options, and dispatches to compare mode if `--compare` is set, single-run mode if `--run-dir` is set, or reports an error otherwise. It writes failures through `mockT.Errorf`; if any failure occurred, `FailNow` exits with status 2.

Persistence and integration: uses the same run directories, history paths, and compare root directories as `internal/metamorphic` tests. It integrates with `metaflags` and `pebble/metamorphic` without a real `testing.T`. Risks include limited test-like behavior in `mockT`, hard process exit on failure, and reliance on run-once flags only. No local tests are included; confidence comes from the shared option builder and use by coverage workflows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metarunner/main.go -->
