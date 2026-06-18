# sources/user-network-fs/rclone/backend/compress/compress_test.go

## Purpose
This file provides integration-style validation for the compress backend through rclone's shared filesystem test suite. It exercises the wrapper against configured remotes and against local temporary directories in gzip and zstd modes.

## Important APIs, types, and functions
`defaultOpt` defines the shared `fstests.Opt`, including `RemoteName`, nil object type, unimplementable fs methods, tiers to test, and object method expectations. `TestIntegration` runs against `TestCompress:`. `TestRemoteGzip` and `TestRemoteZstd` build temporary local-backed compress remotes with mode-specific level config and enable quick tests.

## Control flow
The integration test always calls `fstests.Run` with `defaultOpt`, expecting external configuration. The local gzip and zstd tests are skipped if `fstest.RemoteName` is set, then configure a compress remote over a temp path under `os.TempDir()` using extra config entries. Each test delegates actual behavior validation to `fstests`.

## State and persistence behavior
Local tests persist temporary data under fixed tempdir names such as `rclone-compress-test-gzip` and `rclone-compress-test-zstd`; cleanup depends on the shared test suite and filesystem state. The tests exercise creation of metadata/data object pairs indirectly.

## Dependencies and integration points
The file imports several backends for registration side effects (`drive`, `local`, `s3`, `swift`) and depends on rclone `fstest`/`fstests`. Tier tests imply the wrapper should propagate tier operations when the underlying remote supports them.

## Risks and edge cases
The fixed tempdir names under `os.TempDir()` can retain state across failed runs. The test marks `PutStream` unimplementable in `defaultOpt`, so conditional streaming behavior and compressed final-name renaming are not strongly covered. There are no focused tests for metadata file contents, zstd seek metadata, gzip partial reads, corrupt metadata, orphan cleanup, or MIME detection.

## Test signals
The generic suite provides broad object lifecycle coverage for both gzip and zstd local configurations. It is useful for API compatibility but not sufficient for the backend's two-object persistence invariants.
