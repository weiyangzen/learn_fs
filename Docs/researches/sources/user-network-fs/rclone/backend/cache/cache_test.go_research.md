# sources/user-network-fs/rclone/backend/cache/cache_test.go

## Purpose
This file wires the cache backend into rclone's generic filesystem conformance suite. It provides broad integration coverage for the public `fs.Fs`, `fs.Object`, and `fs.Directory` interfaces implemented by the deprecated cache backend.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestCache:"` and `NilObject: (*cache.Object)(nil)`. It declares methods the backend cannot implement, including `PublicLink`, random-write/chunk-writer APIs, directory metadata mutation, `ListP`, object MIME/ID/tier/metadata methods, and directory metadata/set-modtime methods.

## State And Persistence
The test suite creates and removes objects and directories through the cache remote selected by rclone test configuration. The actual persistent state is owned by the backend under test: Bolt metadata, chunk files, and wrapped remote contents.

## Dependencies And Integration Points
It imports `backend/cache`, blank-imports `backend/local` so local remotes are available, and delegates assertions to `fstest/fstests`. The build tags exclude Plan 9, JavaScript, and race builds.

## Risks And Test Signals
Primary signal is compatibility with rclone's standard backend contract. `SkipInvalidUTF8` documents a known weakness: invalid UTF-8 confuses cache path handling. Because most behavior lives in `fstests.Run`, failures usually indicate interface contract regressions rather than narrow unit failures.
