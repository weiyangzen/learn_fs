<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java

Purpose: Generic base for an open SMB handle, including close, lock/unlock builder support, and file id exposure.

Important APIs/types/functions: requestLock(), lockRequest(List<SMB2LockElement>), getFileId(), close(), closeSilently(), and LockBuilder methods exclusiveLock(), sharedLock(), unlock(), send().

Control flow: LockBuilder accumulates SMB2LockElement records and send() delegates to Open.lockRequest. For dialects newer than SMB 2.0.2, lockRequest takes an OperationBucket for sequence number/index, sends the lock request through Share, then frees the bucket.

State and persistence behavior: Stores share, fileId, name, and OperationBuckets. Lock operations mutate remote byte-range lock state.

Dependencies and integration points: Base class for DiskEntry and NamedPipe. Depends on Share.sendLockRequest(), SMB2LockFlag, SMB2LockElement, SMB2Dialect, and SmbPath.

Risks: OperationBucket is freed only after successful send; exceptions can leak buckets. close() throws runtime SMBApiException from Share without checked signature. LockBuilder can send an empty lock list.

Test signals: Exclusive/shared/unlock flag encoding, failImmediately flag, dialect SMB_2_0_2 sequence zero behavior, exception path bucket leak, closeSilently logging, and empty lock list behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java -->
