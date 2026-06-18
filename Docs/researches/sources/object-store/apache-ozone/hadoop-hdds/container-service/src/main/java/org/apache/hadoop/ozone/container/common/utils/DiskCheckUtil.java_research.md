<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java

## Purpose

`DiskCheckUtil` performs low-level storage directory health checks for existence, permissions, and actual read/write/delete behavior. It also supports test injection of disk-check implementations. The complete 208-line file was read.

## Important APIs, Types, and Functions

Static APIs are `checkExistence`, `checkPermissions`, `checkReadWrite`, `setTestImpl`, and `clearTestImpl`. `DiskChecks` is an injectable interface with default-success methods. `DiskChecksImpl` contains production checks.

## Control Flow

`checkExistence` verifies the directory exists. `checkPermissions` checks read, write, and execute permissions and logs every missing permission before returning a single failure. `checkReadWrite` creates a random test file in the supplied test directory, writes random bytes through `FileUtils.newOutputStreamForceAtClose`, reads the same number of bytes back, compares content, and deletes the file. Each failure logs a volume-specific error and returns false.

## State and Persistence Behavior

The only persistent side effect is a temporary `disk-check-<uuid>` file that should be deleted after a successful check. Failure paths can leave the test file behind when delete is not reached or delete fails. The active implementation is static mutable test state.

## Dependencies and Integration Points

It depends on Java file APIs, Ratis `FileUtils`, and storage volume scanners/checkers that call these utilities. Tests can inject failure behavior through `DiskChecks`.

## Risks and Edge Cases

If `fis.read(readBytes)` returns a short read even though more bytes are available, the method treats it as failure; for local files this is usually acceptable. Delete failure marks the disk unhealthy. Static test implementation must be cleared to avoid cross-test contamination. The SyncFailedException log message says "Could sync" instead of "Could not sync".

## Test Signals

Tests should cover missing directory, each permission bit, write/read content mismatch, short read, delete failure, injected implementations, cleanup/reset of test impl, and leftover temporary file handling on failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/DiskCheckUtil.java -->
