## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedFileChecksumHelper.java

### Purpose
`ReplicatedFileChecksumHelper` specializes `BaseFileChecksumHelper` for replicated keys by retrieving chunk metadata from the DataNode pipeline for each block.

### Important APIs and Types
It provides constructors with and without pre-fetched `OmKeyInfo`, returns `ReplicatedBlockChecksumComputer`, and overrides `getChunkInfos`. It uses `Pipeline.copyForRead`, `ContainerProtocolCalls.getBlock`, block tokens, and xceiver client acquisition/release.

### Control Flow
For each block, it copies the pipeline for read regardless of container state, acquires an xceiver client, calls `getBlock` with the block ID, token, and replica indexes, extracts chunks from the response, and releases the read client in `finally`.

### State and Persistence Behavior
The helper has inherited per-computation state and performs read-only container metadata requests.

### Dependencies and Integration Points
It integrates `BaseFileChecksumHelper` with HDDS container protocol calls for RATIS/STANDALONE-style replicated data. It is the default helper for all non-EC replication types.

### Risks and Edge Cases
Failures in DataNode reads bubble as `IOException`. Correctness depends on `copyForRead` choosing an appropriate readable replica set. The helper assumes returned chunk metadata includes checksum data.

### Test Signals
Tests should verify read pipeline copying, token and replica-index propagation, client release on errors, empty chunk response handling via base class, and final checksum integration for replicated keys.
