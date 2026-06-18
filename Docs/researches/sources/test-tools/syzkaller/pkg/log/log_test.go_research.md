## sources/test-tools/syzkaller/pkg/log/log_test.go

Purpose: tests log caching behavior and lazy formatting.

Important APIs/types/functions: test `init`, `TestCaching`, `TestLazy`, and `noFormat`.

Control flow: enables a 4-line/20-byte cache, disables timestamp prefix, writes messages of increasing sizes, checks exact cached output, and verifies a disabled verbose log does not call `String`.

State and persistence: mutates package global cache and `prependTime`.

Dependencies and integration: package-level tests access unexported globals.

Risks: global one-shot cache setup can interact with other tests if package changes.

Test signals: strong unit coverage for cache eviction and lazy formatting semantics.
