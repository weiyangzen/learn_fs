# sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler_test_wrapper.go

Purpose: fuse2-specific test helper file that defines the shared `libfuseTestSuite` scaffolding and callback helper functions used by `libfuse_handler_test.go` when built with the `fuse2` tag.

Important APIs/types/functions: `libfuseTestSuite` owns assertions, a `*Libfuse`, gomock controller, and `internal.MockComponent`. `fileHandle` mirrors the C native file-handle layout enough for tests to recover the Go handle pointer from `fi.fh`. `newTestLibfuse`, `SetupTest`, `setupTestHelper`, and `cleanupTest` configure a libfuse component without starting a real mount and assign global `fuseFS`. Helper functions include `testMkDir`, `testStatFs`, `testRmDir`, `testCreate`, `testOpen`, open-flag variations, `testTruncate`, no-op ftruncate tests, `testUnlink`, `testSymlink`, `testReadLink`, `testFsync`, `testFsyncDir`, `testChmod`, `testChown`, and `testUtimens`.

Control flow: each helper creates C strings and FUSE file-info structs, sets gomock expectations on the mock component, invokes the exported cgo callback directly, and asserts the returned C errno-style value. Open/create helpers let the callback allocate a native file object and then inspect its embedded Go handle pointer for fsync tests. Config-specific helpers tear down and rebuild the suite libfuse with custom YAML to test open-flag settings.

State and persistence behavior: no real filesystem persistence is used. State is held in gomock expectations, `handlemap`, allocated C strings/native file objects, and global `fuseFS`. Helpers call `cleanupTest` with `defer`, causing gomock verification after each helper. Since `Start` is not called, stats collector assumptions can matter if callback code updates stats; tests rely on package/test setup providing enough global state or paths that do not dereference nil stats in this environment.

Dependencies/integration points: depends on fuse2 cgo headers, `libfuse_wrapper.h`, `internal.MockComponent`, `handlemap`, global config reader, logging, `testify`, and the callback implementations in `libfuse2_handler.go`. The common `libfuse_handler_test.go` file calls these helper functions to avoid duplicating tests between fuse2 and fuse3 builds.

Risks: this is a wrapper rather than a full integration test; it bypasses libfuse's real C dispatch, kernel behavior, mount lifecycle, extension flow, and many native file I/O paths. There is a TODO for readdir tests. Helpers often return empty handles, which may not represent realistic cached/noncached handle state. Some tests do not release allocated native handles after open/create.

Test signals: validates callback-to-component option construction and errno mapping for common operations under fuse2. It specifically documents fuse2's lack of writeback-cache append-flag rewriting and fuse2's no-op ftruncate test behavior.
