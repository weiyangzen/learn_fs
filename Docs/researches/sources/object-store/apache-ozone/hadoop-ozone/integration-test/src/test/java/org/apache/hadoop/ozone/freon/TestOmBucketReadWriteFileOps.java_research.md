# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteFileOps.java

## Purpose
This abstract non-HA integration test validates the Freon `obrwf` command, which performs mixed read/write file operations through the Hadoop `FileSystem` interface against an Ozone bucket path. It checks that the command creates the expected read and write path structures and that OM lock metrics remain healthy.

## Important APIs, Types, and Functions
- `parameters()` builds six `OmBucketTestUtils.ParameterBuilder` scenarios covering default read/write mix, nested prefixes, root prefix, small objects, pure reads, and pure writes.
- `testOmBucketReadWriteFileOps(...)` creates a volume/bucket, constructs an `o3fs://bucket.volume/prefix` root, runs `new Freon().getCmd().execute("obrwf", ...)`, and validates the resulting filesystem entries.
- `verifyFileCreation(...)` counts either directories or files in a `FileStatus[]`.
- `verifyOMLockMetrics(...)` is called on OM metadata lock metrics after Freon execution.

## Control Flow
For each parameter set, the test creates the target bucket, passes OM address and Freon command-line options for counts, data size, buffer size, length, total threads, read-thread percentage, read operations, write operations, and one run. It then opens a Hadoop `FileSystem` for the O3FS URI, lists the root, `readPath`, and `writePath`, and compares directory/file counts against the builder's expected values.

## State and Persistence Behavior
The command creates actual keys/files in Ozone and materializes namespace entries visible through the Hadoop filesystem adapter. The test relies on OM metadata state being updated consistently enough for `listStatus` calls to observe `readPath` and `writePath` contents immediately after command completion.

## Dependencies and Integration Points
Dependencies include `NonHATests.TestCase` for cluster provisioning, Ozone client creation, `TestDataUtil.createVolumeAndBucket`, Freon command dispatch, `OZONE_OM_ADDRESS_KEY`, Hadoop `FileSystem`, O3FS URI handling, and OM lock metrics.

## Risks and Test Signals
Risks include command-line option drift, expected write-count semantics changing for pure read/write cases, and path normalization differences for root and trailing-slash prefixes. The main signals are exact counts in root/read/write directories and successful OM lock metric verification.
