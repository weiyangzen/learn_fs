# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test.go

Purpose: shared libfuse test suite that validates component configuration and calls version-specific callback helper functions supplied by the active build's test wrapper.

Important APIs/types/functions: methods on `libfuseTestSuite` include `TestDefault`, `TestConfig`, `TestConfigZero`, `TestConfigDefaultPermission`, `TestConfigDisableKernelCache`, `TestConfigFuseTraceEnable`, `TestDisableWritebackCache`, `TestIgnoreAppendFlag`, and a matrix of callback tests delegating to helpers such as `testMkDir`, `testRmDir`, `testCreate`, `testOpen`, `testTruncate`, `testUnlink`, `testSymlink`, `testReadLink`, `testFsync`, `testFsyncDir`, `testChmod`, `testStatFs`, `testChown`, and `testUtimens`. `TestLibfuseTestSuite` registers the suite with `testify`.

Control flow: config tests tear down the default setup and recreate libfuse with YAML snippets to assert resolved fields. Callback tests are thin wrappers; the actual gomock expectations and C callback invocations live in version-specific `*_handler_test_wrapper.go` files selected by build tags. This keeps behavior expectations common while adapting cgo signatures for fuse2/fuse3.

State and persistence behavior: no real mount or storage persistence. Tests mutate global config and, for foreground trace, `common.ForegroundMount`. They assert `Libfuse` struct state and callback return values rather than persisted filesystem artifacts. The wrapper tests set package-global `fuseFS` to the test component.

Dependencies/integration points: depends on `testify/suite`, common permission defaults/global foreground flag, `io/fs` mode values, and the active build's wrapper helper functions. It indirectly integrates with gomock internal component mocks and cgo callback implementations.

Risks: because tests do not start `Libfuse.Start`, they do not validate real mount startup, extension loading, capability negotiation, or stats collector lifecycle. Callback coverage omits read, write, flush, release, and readdir paths. Global `common.ForegroundMount` is reset manually and could leak if a test panics before reset. The same test file serves both fuse versions, so version-specific expectations must remain in wrappers.

Test signals: strong for configuration defaults and option precedence: allow-other permissions, direct I/O timeout zeroing, default-permission override, disable-kernel-cache forcing direct I/O, foreground-only trace, writeback-cache toggle, and ignore-open-flags toggle. Callback signals cover common errno mapping and option construction for many metadata operations.
