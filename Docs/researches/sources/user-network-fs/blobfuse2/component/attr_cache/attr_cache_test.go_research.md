# sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache_test.go

Purpose: provides the primary unit test suite for the `attr_cache` component. It uses gomock to isolate the next pipeline component and testify suite/assertions to verify cache mutations after each filesystem method.

Important APIs/types/functions: `attrCacheTestSuite` owns assertions, the `AttrCache` under test, gomock controller, and `internal.MockComponent`. Helpers include `newTestAttrCache`, `getPathAttr`, `addPathToCache`, `assertDeleted`, `assertInvalid`, `assertUntouched`, `assertAttributesTransferred`, `assertSrcAttributeTimeChanged`, `generateNestedDirectory`, `generateNestedPathAttr`, and `addDirectoryToCache`. Tests are grouped by component method: config tests, directory operations, listing, file operations, `GetAttr`, timeout and cleanup, links, chmod, and chown.

Control flow: each test constructs a cache connected to a mock next component, seeds `cacheMap` where needed, sets gomock expectations for success or failure, invokes the attr-cache method, then inspects cache entries directly. Many tests loop over both `a` and `a/` to validate path truncation. Nested directory fixtures intentionally include `a`, children under `a/`, sibling prefix `ab`, and sibling file `ac` to detect accidental prefix overmatching.

State and persistence behavior: tests directly manipulate in-memory `cacheMap` and rely on `Start`/`Stop` to create and tear down the cleanup goroutine. They exercise negative entries, invalid entries, positive attr entries, timeout-driven cleanup, and config-derived fields such as `cacheTimeout`, `maxFiles`, and `noSymlinks`. No persistent state is involved.

Dependencies/integration: imports the repository's `common`, `config`, `log`, `internal`, and `handlemap` packages plus gomock and testify. The suite expects generated mocks for `internal.Component`. The silent logger avoids noisy test output; config is loaded from strings via `config.ReadConfigFromReader`.

Risks: the tests inspect private fields because they are in the same package, which is useful for cache correctness but couples tests to representation. Some assertions rely on wall-clock sleeps for timeout cleanup and may be timing-sensitive. The tests do not appear to run with race detection or assert lock correctness, leaving the RLock-while-mutating risk in the implementation uncovered. `getPathAttr` accepts a `metadata` parameter but does not set metadata, suggesting older metadata-specific behavior may have been simplified without test helper cleanup.

Test signals: strong coverage exists for cache invalidation semantics, deleted-entry ENOENT behavior, cleanup expiry, and path-prefix correctness. Coverage is weaker for concurrent access, `maxFiles` enforcement under concurrency, dynamic config reload, and the unused `no-cache-on-list` setting.
