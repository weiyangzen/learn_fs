# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsage.java

## Purpose

This class tests `DedicatedDiskSpaceUsage` against a real temporary directory with a created file.

## Important APIs, Types, And Functions

It reuses `TestDU.createFile`, constructs `new DedicatedDiskSpaceUsage(dir)`, and asserts `getUsedSpace()`.

## Control Flow

The test writes a 1024-byte file into the temp directory, creates the subject, and asserts that observed used space is at least `FILE_SIZE - 20`, matching a Hadoop Common test tolerance.

## State And Persistence

State is real temporary filesystem content. There is no explicit persistent metadata beyond the temp file.

## Dependencies And Integration Points

The class integrates with JUnit temp directories, `DedicatedDiskSpaceUsage`, `SpaceUsageSource`, and `TestDU`'s file creation helper.

## Risks

The test is environment-sensitive because actual filesystem accounting may differ by platform or mount options. It does not assert capacity or available-space behavior.

## Test Signals

The key signal is `getUsedSpace()` reflecting the created file within the lower-bound tolerance.
