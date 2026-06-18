# sources/test-tools/syzkaller/pkg/aflow/test_util.go

Purpose: provides `NewTestContext`, a small helper for internal aflow and tool unit tests that need a cache-backed context.

Important APIs/functions: `NewTestContext(t *testing.T) *Context` creates a temporary cache with `NewCache(t.TempDir(), 10000000)` and returns `&Context{cache: cache}`.

Control flow: the helper fails the test immediately if cache creation fails, then leaves other `Context` fields unset for the caller to populate as needed.

State and persistence: uses the test framework's temporary directory for cache storage. The cache is bounded by the hard-coded size parameter and is cleaned with the test tempdir lifecycle.

Dependencies and integration: imports `testing` and testify `require`. Integrates with tool/action tests that need real cache behavior but do not need full flow execution.

Risks and test signals: the returned context is intentionally partial; tests that require `Workdir`, cancellation, event callbacks, or stubs must set them explicitly. The helper centralizes cache setup so cache API changes affect fewer tests.
