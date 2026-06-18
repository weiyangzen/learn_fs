## sources/user-network-fs/gcsfuse/cfg/config_util_test.go

Purpose: Unit tests for derived defaults and config utility predicates.

Important APIs/types/functions: tests include `Test_DefaultMaxBackground`, `Test_DefaultCongestionThreshold`, `Test_DefaultMaxParallelDownloads`, `TestIsFileCacheEnabled`, `TestIsParallelDownloadsEnabled`, `Test_ListCacheTtlSecsToDuration`, `Test_ListCacheTtlSecsToDuration_InvalidCall`, `TestIsTracingEnabled`, `TestIsMetricsEnabled`, `TestIsGKEEnvironment`, and `TestGetBucketType`.

Control flow: table-driven assertions cover positive/negative feature states and priority rules; invalid TTL test uses `recover` to assert panic.

State and persistence: no persistent state; some tests run in parallel.

Dependencies and integration points: validates `config_util.go`, constants from `constants.go`, and validation behavior from `validate.go`.

Risks: default tests assert broad bounds rather than exact values because defaults vary by machine CPU count. Parallel tests use independent configs and are safe.

Test signals: good coverage for utility semantics that affect mounting, caching, metrics, tracing, and optimization bucket classification.
