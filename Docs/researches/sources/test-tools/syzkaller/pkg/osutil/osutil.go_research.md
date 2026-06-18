# sources/test-tools/syzkaller/pkg/osutil/osutil.go

Purpose: Core OS utility package for subprocess execution, file/path helpers, JSON helpers, atomic writes, gzip writing, temp files, absolute paths, monotonic time, and recursive disk usage.

Important APIs: `RunCmd`, `Run`, `CommandContext`, `Command`, `GraciousCommand`, `VerboseError`, `VerboseMessage`, `IsExist`, `FilesExist`, `CopyFiles`, `CopyDirRecursively`, `LinkFiles`, `MkdirAll`, `WriteFile`, `WriteFileAtomically`, `WriteJSON`, `ReadJSON`, `ParseJSON`, `JSONDeepCopy`, `WriteGzipStream`, `WriteExecFile`, `TempFile`, `TempFileIn`, `ListDir`, `Abs`, `FileTimes`, `MonotonicNano`, and `DiskUsage`.

Control flow: Command helpers set platform death-signal behavior, kill process groups on timeout/cancel, and return combined output with `VerboseError` on failure. Copy/link helpers expand slash-form glob patterns from a source tree into a destination tree, with required/optional pattern handling. JSON parsing disallows unknown fields. `Abs` caches the initial working directory and panics if it changes. `DiskUsage` walks recursively and sums platform-specific usage.

State and persistence: Performs real filesystem and process mutations. Uses package-level cached working directory and `sync.Once`.

Dependencies and integration: Heavily used by manager config, diff patch scanning, report decompilation, coverage, crash storage, VM setup, tests, and cron-like helpers.

Risks: `Run` with zero timeout times out immediately. `WriteFileAtomically` uses a fixed `.tmp` suffix and can conflict with concurrent writers. `Abs` intentionally panics if cwd changes, which enforces process invariants but surprises libraries. `CopyFiles` removes destination before rename, so replacement is not fully atomic on Linux.

Test signals: `osutil_test.go` covers existence checks, copy/link glob behavior, monotonic time, JSON round-trip, disk usage on Linux, and verbose error formatting.
