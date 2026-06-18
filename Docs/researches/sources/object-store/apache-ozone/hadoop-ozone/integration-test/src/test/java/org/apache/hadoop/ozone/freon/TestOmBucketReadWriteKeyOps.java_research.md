# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteKeyOps.java

## Purpose
This abstract non-HA integration test validates Freon's `obrwk` command for direct Ozone key operations. It covers mixed read/write, pure read, pure write, varying key lengths, zero-byte objects, buffer size, and thread-mix behavior in an `OBJECT_STORE` bucket.

## Important APIs, Types, and Functions
- `setup()` and `cleanup()` manage one `OzoneClient` per test method.
- `parameters()` returns six `ParameterBuilder` cases for command-line coverage.
- `testOmBucketReadWriteKeyOps(...)` creates an object-store bucket, runs `new Freon().getCmd().execute("obrwk", ...)`, measures elapsed monotonic time, validates key counts, and checks lock metrics.
- `verifyKeyCreation(...)` lists keys under `/readPath/` or `/writePath/` and asserts exact counts.

## Control Flow
The test creates a volume and bucket with `BucketLayout.OBJECT_STORE`, executes Freon with OM address, volume, bucket, read key count, write key count, data size, buffer, key length, thread count, read percentage, read/write operation counts, and run count. After the command returns, it iterates keys under read and write prefixes and compares counts with expected values.

## State and Persistence Behavior
The command persists OM key-table entries under stable `/readPath/` and `/writePath/` prefixes. The test does not inspect block data content; it uses key namespace visibility and Freon counters as the state signal.

## Dependencies and Integration Points
The file integrates `NonHATests.TestCase`, `TestDataUtil`, `OzoneBucket.listKeys`, Picocli-backed Freon command dispatch, OM config address injection, `BucketLayout.OBJECT_STORE`, and `OmBucketTestUtils.verifyOMLockMetrics`.

## Risks and Test Signals
Risks include prefix normalization with leading slashes, concurrency-sensitive key counts, and expected-write-count logic in `ParameterBuilder`. Signals are exact read/write prefix counts and clean OM lock metrics after threaded command execution.
