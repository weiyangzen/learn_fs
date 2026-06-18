# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DBOptionsTest.java

## Purpose

Broad JNI contract coverage for `DBOptions`, including copy construction, properties parsing, environment and IO controls, WAL/log/manifest settings, write scheduling, caches, WAL filters, rate limiting, stats, recovery toggles, DB ID persistence, listeners, and nested native object ownership.

## Important APIs, control flow, and dependencies

The file exercises `DBOptions`, `ConfigOptions`, `Env`, `RocksEnv`, `DbPath`, `WriteBufferManager`, `Cache`, `AbstractWalFilter`, `RateLimiter`, `SstFileManager`, `Statistics`, and `AbstractEventListener`. Most tests set one field and assert the getter. Property tests cover valid props and null/empty/unknown failures. Nested-resource tests attach envs, row caches, write buffer managers, WAL filters, rate limiters, SST file managers, statistics, and listener lists.

## State, persistence, risks, and test signals

No DB is generally opened, but these options control persistent behavior such as WAL recovery, manifest DB ID writing, log directories, WAL directories, atomic flush, two write queues, and best-effort recovery. The listener test is notable: it verifies list replacement does not invalidate previously returned Java listener references. Risks include stale option names, long/int truncation, enum drift, child-wrapper lifetime bugs, and listener list ownership mistakes. Signals are exact defaults, fluent return identity, getter equality, and expected exceptions for invalid properties.
