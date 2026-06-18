## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ChecksumHelperFactory.java

### Purpose
`ChecksumHelperFactory` selects the file-checksum helper implementation based on replication type.

### Important APIs and Types
`getChecksumHelper` accepts replication type, volume, bucket, key name, length, combine mode, client protocol, and `OmKeyInfo`. It returns `ECFileChecksumHelper` for `HddsProtos.ReplicationType.EC` and `ReplicatedFileChecksumHelper` otherwise.

### Control Flow
The factory performs a single conditional on replication type and constructs the appropriate helper.

### State and Persistence Behavior
The class is stateless and has a private constructor.

### Dependencies and Integration Points
It is called by `OzoneClientUtils.getFileChecksumWithCombineMode` after OM key lookup. It integrates EC and replicated checksum implementations behind the common `BaseFileChecksumHelper` abstraction.

### Risks and Edge Cases
All non-EC replication types are treated as replicated. New replication types would need review to ensure this fallback is correct.

### Test Signals
Tests should verify EC selection, RATIS/STANDALONE replicated selection, and constructor argument propagation through helper behavior.
