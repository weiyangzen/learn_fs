# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptionsInterface.java

Purpose: generic fluent contract for database-wide option types. `T extends DBOptionsInterface<T>` allows setters to return the concrete option type while sharing API documentation across `DBOptions` and related composite option classes.

The interface declares the DB-level option surface: environment, parallelism, creation/open flags, rate limiting, SST manager, logging, statistics, fsync, DB/WAL paths, obsolete-file cleanup, background job/subcompaction controls, log/manifest/WAL sizes, direct/mmap IO, file allocation, stats dump/persist/history, write buffer manager, event listeners, write pipeline/concurrency/yield settings, WAL recovery/2PC, caches/filters, recovery/flush behavior, ingest/atomic flush, stats-to-disk, DB ID manifest, log readahead, best-efforts recovery, background-error retry, and daily off-peak time.

Control flow is declarative only; implementations supply native forwarding. State and persistence behavior are described in comments and realized by implementers and native RocksDB. Dependencies include many RocksDB Java types and option consumers.

Risks: documentation drift from `DBOptions` or C++ defaults, default/deprecated behavior ambiguity, and generic implementers missing newly added methods. Tests should compile all implementers, run documentation-backed round-trips in `DBOptions`, and verify new methods are added consistently to implementations and JNI.
