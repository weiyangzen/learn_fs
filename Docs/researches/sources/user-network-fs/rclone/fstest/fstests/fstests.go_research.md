
# sources/user-network-fs/rclone/fstest/fstests/fstests.go

Purpose: package `fstests` is rclone's generic backend integration-test suite for `fs.Fs`, `fs.Object`, and `fs.Directory` behavior. It is intended to be imported by backend tests and exercises the common contract that every backend should meet: remote creation/removal, listings, object reads/writes, metadata, modtimes, optional feature methods, wrapper completeness, chunked uploads, bucket edge cases, and shutdown behavior.

Important APIs/types/functions: `InternalTester` lets a backend add backend-specific checks. `ChunkedUploadConfig`, `SetUploadChunkSizer`, `SetUploadCutoffer`, and `SetCopyCutoffer` provide test-only tuning hooks for multipart upload/copy sizing. `NextPowerOfTwo`, `NextMultipleOf`, `PutTestContentsMetadata`, `PutTestContents`, `TestPutLarge`, `TestPutLargeStreamed`, and `ReadObject` are reusable helpers. `Opt` carries backend-specific skips and capability settings. The central API is `Run(t, opt)`.

Control flow: `Run` initializes fstest config, optionally starts a `testserver`, creates a randomized remote via `fs.NewFs`, then builds a deeply nested `t.Run` tree. Early tests validate core `Fs` identity and empty directory behavior; nested tests create directories and objects before exercising list, copy, move, purge, object metadata, public links, tiering, bucket-based path edge cases, stream/unknown-size upload, directory metadata, and final purge. Tests frequently skip based on `fs.Features()` capabilities rather than failing unsupported optional interfaces.

State/persistence: the suite creates temporary remote trees and local state, writes random test objects, changes global config flags such as `Metadata` and `UseListR` in scoped contexts, and stores `InternalTestFiles` for backend-specific internal tests. Cleanup purges the remote at the end and removes local temp directories for local remotes. Eventual consistency is handled with retries and listing retry flags.

Dependencies/integration: heavily integrated with `github.com/rclone/rclone/fs`, `cache`, `config`, `fspath`, `hash`, `object`, `operations`, `walk`, `fstest`, and `testserver`. It relies on `testify` assertions, random content generation, rclone encoders, and fs feature flags as the negotiated capability contract.

Risks: because this file mutates live remotes, failures can leave remote objects behind if cleanup is interrupted. Tests involving public links, metadata, directory modtimes, chunked uploads, and change notification are backend-sensitive and can be flaky under eventual consistency. Several skips and backend-specific bypasses indicate known feature gaps. A duplicated `unwrappableFsMethods` initializer appears in the read source and should be checked if compiling this exact tree.

Test signals: the file is itself a test harness; success means a backend satisfies broad rclone interface semantics. Failures are intentionally granular through nested test names such as `FsMkdir/FsPutFiles/ObjectOpenRange`, which feed the retry/re-run machinery in `fstest/runs`.
