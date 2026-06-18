# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDU.java

## Purpose

This class tests the `DU` disk-usage source against real temporary files on non-Windows platforms, including exclude-pattern behavior.

## Important APIs, Types, And Functions

`createFile(File, int)` writes random data via `RandomAccessFile` and syncs it to disk. `testGetUsed()` constructs `new DU(file)`. `testExcludePattern()` constructs `new DU(dir, "*.tmp")`. `assertFileSize()` accepts filesystem slack of 8 KiB.

## Control Flow

`setUp()` skips tests on Windows. Test files are created with random bytes to avoid compression. The subject queries disk usage and assertions compare observed usage with expected written sizes.

## State And Persistence

State is real temporary filesystem state under JUnit `@TempDir`. Files are created and flushed, then removed by the test framework.

## Dependencies And Integration Points

The test integrates with Hadoop `Shell.WINDOWS`, Ozone `KB`, Commons `RandomUtils`, Java file IO, and the production `DU` implementation.

## Risks

Disk usage depends on filesystem block size, metadata overhead, compression, sparse-file behavior, and platform availability of `du`; the slack allowance mitigates but does not eliminate environment sensitivity.

## Test Signals

Signals are used-space values at least the expected written size and no more than expected plus 8 KiB, and exclusion of matching `*.tmp` files from directory totals.
