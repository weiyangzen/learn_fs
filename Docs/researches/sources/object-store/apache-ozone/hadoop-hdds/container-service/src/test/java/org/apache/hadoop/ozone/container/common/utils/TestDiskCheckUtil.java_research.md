# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestDiskCheckUtil.java

## Purpose
Tests `DiskCheckUtil` low-level predicates for permissions, directory existence, and read/write probe cleanup.

## Important APIs, Types, And Functions
`DiskCheckUtil.checkPermissions`, `checkExistence`, and `checkReadWrite` are exercised against a JUnit `@TempDir`.

## Control Flow
The test toggles read, write, and execute bits off and back on, deletes the temp directory for existence failure, and runs a 10-byte read/write probe.

## State And Persistence
Only temporary directory permissions and probe files are mutated. Successful read/write checks must remove probe files.

## Dependencies And Integration Points
Provides utility coverage for volume health checks that depend on `DiskCheckUtil`.

## Risks And Edge Cases
Permission mutation can behave differently on non-POSIX filesystems or privileged runs. The test assumes Java `File` permission setters succeed.

## Test Signals
Boolean assertions and an empty temp directory after the probe show failure detection and cleanup.
