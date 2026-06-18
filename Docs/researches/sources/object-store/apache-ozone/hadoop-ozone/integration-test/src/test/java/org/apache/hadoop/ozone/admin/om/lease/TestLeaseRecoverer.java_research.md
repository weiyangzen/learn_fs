# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/admin/om/lease/TestLeaseRecoverer.java

## Purpose
`TestLeaseRecoverer` verifies the OM admin lease-recovery CLI against an FSO bucket in a non-HA Ozone cluster. It creates an open file, writes and syncs data, runs `LeaseRecoverer --path`, and then confirms the recovered file is visible, closed, immutable through the old output stream, and safely recoverable a second time.

## Important APIs, Types, and Functions
- The abstract test implements `NonHATests.TestCase`, using `cluster()` supplied by the concrete non-HA test harness.
- `TestDataUtil.createVolumeAndBucket(client, BucketLayout.FILE_SYSTEM_OPTIMIZED)` creates the target FSO bucket.
- `FileSystem`, `FSDataOutputStream`, `FileStatus`, `LeaseRecoverable`, and `Path` exercise the OFS filesystem path.
- `CommandLine(new LeaseRecoverer()).setOut(...).setErr(...)` invokes the picocli admin command in-process.
- Constants `OZONE_OFS_URI_SCHEME`, `OZONE_URI_DELIMITER`, and `OZONE_OM_ADDRESS_KEY` build the OFS URI.

## Control Flow
`init` creates an Ozone client and an FSO bucket. `testCLI` builds an `ofs://<om-address>/<volume>/<bucket>/file` path and opens a Hadoop `FileSystem` for the OFS root. `testWithFS` writes random bytes to a new file, calls `hsync`, executes the lease-recovery command with `--path`, checks stderr is empty, and asserts the visible file length equals the first write. It then attempts another write through the old stream; `flush` and `hsync` must throw `IOException`, length must remain unchanged, `isFileClosed` must report true, close must succeed, and a second CLI recovery call must also succeed without stderr.

## State and Persistence Behavior
The test persists a volume, FSO bucket, and file through the cluster's OM and filesystem implementation. Lease recovery transitions the key/file from an open lease to closed state, after which the old stream can no longer extend committed length. The second command execution validates idempotence.

## Dependencies and Integration Points
The file connects the admin CLI, OFS URI parsing, Hadoop `FileSystem`, FSO bucket layout, OM lease recovery, and stream failure handling. It uses picocli output redirection to assert CLI cleanliness without spawning a separate process.

## Risks and Edge Cases
The test is non-HA only and focuses on FSO layout, not object-store bucket layout. It assumes `flush` after recovery will call writeChunk/putBlock and fail; changes in stream buffering could alter where the exception appears. It checks stderr but does not inspect stdout or command exit code. Random content validates length, not byte-for-byte data after recovery.

## Test Signals
Passing means the lease-recovery CLI closes an open OFS file, preserves the last synced length, rejects further writes through the stale stream, reports the file as closed, and remains idempotent on repeated recovery.
