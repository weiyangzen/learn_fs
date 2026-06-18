<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java

Purpose: Allocates up to 64 operation buckets for SMB lock sequence numbers and indexes.

Important APIs/types/functions: takeFreeBucket() returns an existing free bucket or creates a new one up to 64. freeBucket(int) marks by one-based index free and increments sequenceNumber. OperationBucket exposes getIndex() and getSequenceNumber().

Control flow: Open.lockRequest takes a bucket before sending a lock for newer dialects, passes bucket sequence number/index, then frees it.

State and persistence behavior: In-memory list of buckets protected by ReentrantReadWriteLock write lock.

Dependencies and integration points: Package-private helper for Open.

Risks: freeBucket uses `sequenceNumber += 1 % 16`, which increments by one because modulo binds first; it likely intended `(sequenceNumber + 1) % 16`. Sequence numbers will not wrap at 16. Exceptions between take and free in Open can exhaust buckets. No validation for invalid free index.

Test signals: Allocate 64 buckets, exhaustion error, reuse freed bucket, sequence wrap expectation, invalid index, and exception path from Open.lockRequest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java -->
