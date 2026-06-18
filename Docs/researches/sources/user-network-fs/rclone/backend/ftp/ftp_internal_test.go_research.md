# sources/user-network-fs/rclone/backend/ftp/ftp_internal_test.go

## Purpose
This internal test file adds FTP-specific checks that run through rclone's `fstests.InternalTester` hook against real configured FTP remotes.

## Important APIs, Types, And Control Flow
`deriveFs` builds a derived remote string from the current test remote plus injected config options. `testUploadTimeout` creates a 100 MiB pattern reader and uploads it through a derived backend with controlled `concurrency` and `shut_timeout`, temporarily lowering global low-level retries and the I/O timeout after the initial control connection is established. It fails if upload blocks beyond a hard deadline. `testTimePrecision` normalizes hashed test remote names and asserts ProFTPd, PureFTPd, and VsFTPd precision is at most one second. `InternalTest` dispatches both tests.

## State And Persistence
The tests mutate global `fs.ConfigInfo` retry and timeout settings during execution and restore them with `defer`. They create a large remote test object and remove it afterward when upload succeeds. No local persisted state is created.

## Dependencies And Integration Points
The file depends on `fstests`, `fstest`, `object.NewStaticObjectInfo`, `readers.NewPatternReader`, config maps, and testify assertions. It exercises the production FTP backend through `fs.NewFs`, not by direct mocks.

## Risks And Test Signals
The upload timeout test is intentionally skipped in `testing.Short` because it is large and timing-sensitive. It targets deadlocks or I/O timeouts around data connection shutdown and concurrency tokens. The precision test documents the expected behavior for common FTP daemons and guards regressions in feature detection for `Precision`.
