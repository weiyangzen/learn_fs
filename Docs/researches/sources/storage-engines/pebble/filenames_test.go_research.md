# sources/storage-engines/pebble/filenames_test.go

## Purpose
Tests filename and marker-file crash recovery around `CURRENT`/MANIFEST updates, specifically ensuring temporary files left behind by a failed atomic marker rename are cleaned on the next successful `Open`. It also benchmarks filename formatting for table and blob file numbers.

## Important APIs, Types, And Functions
`TestSetCurrentFileCrash` is the primary test. `allTempFiles` lists the filesystem and filters entries through `base.ParseFilename` for `FileTypeTemp`. `renameErrorFS` injects rename failures by wrapping `vfs.FS.Rename`. `noFatalLogger` logs fatal messages to `testing.T` instead of aborting. `BenchmarkMakeFilename` repeatedly calls `base.MakeFilename` for table/blob file types.

## Control Flow
The test opens and closes a fresh DB to create an initial manifest, reopens through `renameErrorFS` with `MaxManifestFileSize` set tiny to force a manifest roll, expects the configured rename error, then checks that a temp file remains. A third open with the normal memory filesystem must succeed and remove the temp marker files before close.

## State And Persistence Behavior
All state lives in a `vfs.NewMem` filesystem. The test intentionally leaves a temporary file from a failed marker rename, then verifies open-time cleanup removes it. This covers persistence hygiene during manifest roll crashes: the durable DB state must still be recoverable, and stale temp files must not accumulate or confuse filename parsing.

## Dependencies And Integration Points
The file relies on Pebble `Open`/`Close`, manifest rolling through `MaxManifestFileSize`, `base.ParseFilename`, `base.MakeFilename`, `vfs.FS`, and logger behavior. It is adjacent to the atomic marker machinery used for `CURRENT` and format-version marker files.

## Risks And Edge Cases
The simulated crash is a rename failure in the middle of a marker update. If cleanup is incomplete, later opens may leave stale temp files, and if fatal logging panics the test cannot observe the intended recovery path. The benchmark also indirectly protects against avoidable allocation or formatting regressions in hot filename construction.

## Test Signals
Signals are the expected injected rename error, at least one temp file after the failed open, zero temp files after the normal reopen, no fatal panic through `noFatalLogger`, and benchmark performance for `base.MakeFilename`.
