# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchThreadedTest.java

## Purpose

This parameterized test stresses concurrent Java `WriteBatch` creation and `RocksDB.write` calls with different thread counts.

## Important APIs and types

It uses JUnit parameterization, `RocksDB`, `Options.setIncreaseParallelism`, `WriteBatch`, `WriteOptions`, `ByteBuffer`, `ExecutorService`, `ExecutorCompletionService`, `Callable`, and `Future`.

## Control flow

For thread counts 1, 10, 50, and 100, setup opens a DB with increased parallelism. The test creates 100 callables; each builds a write batch with 100 integer keys and writes it. Submitted tasks are consumed through completion service; on the first execution failure, remaining futures are cancelled and the exception is rethrown. Teardown closes the DB.

## State and persistence behavior

Each task persists 100 records through a batch write, for 10,000 total writes per parameter. The test does not read them back; it treats absence of concurrency exceptions as success.

## Dependencies and integration points

This exercises thread-safety boundaries around independent `WriteBatch` objects, shared `RocksDB.write`, write options, JNI calls from multiple Java threads, and DB internal write serialization.

## Risks and test signals

Risks include races in shared DB native handle use, write-batch native allocation under load, executor shutdown timing, and missing data validation. The signal is successful completion of all futures without `ExecutionException`.
