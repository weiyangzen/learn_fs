# sources/storage-engines/rocksdb/test_util/testharness.h

Purpose: declares RocksDB's gtest convenience layer: skip/bypass macros, status assertions, temporary path helpers, random seed and memory gates, and regex matching assertions.

Important APIs/macros: `ROCKSDB_GTEST_SKIP()` uses `GTEST_SKIP_` when available and otherwise records success while printing to stderr. `ROCKSDB_GTEST_BYPASS()` marks intentionally omitted parameterizations. `ASSERT_OK`, `EXPECT_OK`, `ASSERT_NOK`, and `EXPECT_NOK` wrap `Status`. `EXPECT_NEAR2` avoids integer precision warnings. `TestRegex`, `ASSERT_MATCHES_REGEX`, and `EXPECT_MATCHES_REGEX` provide whole-string regex checks.

State and integration: no persistent state. Declarations integrate with `Env`, gtest, and `port/stack_trace.h`. `using test::TestRegex` exposes the helper in the RocksDB namespace.

Risks and test signals: skip macros do not themselves return from tests, so callers must return after invoking them. Regex constructors can throw on bad patterns. Tests should verify status failure output, skip behavior on gtest versions with and without real skip support, and regex whole-match semantics.
