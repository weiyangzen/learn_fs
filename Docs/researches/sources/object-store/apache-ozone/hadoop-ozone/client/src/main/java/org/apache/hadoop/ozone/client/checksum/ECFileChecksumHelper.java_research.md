## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECFileChecksumHelper.java

### Purpose
`ECFileChecksumHelper` specializes file checksum computation for erasure-coded keys by retrieving the chunk metadata needed to compute EC stripe checksums.

### Important APIs and Types
It extends `BaseFileChecksumHelper`, returns `ECBlockChecksumComputer`, and overrides `getChunkInfos`. It uses `ECReplicationConfig`, `StandaloneReplicationConfig`, `Pipeline`, `ContainerProtocolCalls.getBlock`, and block tokens.

### Control Flow
For each `OmKeyLocationInfo`, it selects DataNodes whose replica index is `1` or greater than the EC data count, because stripe checksum information needed for file checksum is stored on replica index 1 and parity nodes. It rebuilds the pipeline as a standalone factor-three pipeline over those nodes, acquires an xceiver client for read, calls `getBlock` with block ID, token, and replica indexes, then releases the client in a `finally` block.

### State and Persistence Behavior
The helper has the state inherited from `BaseFileChecksumHelper`. It does not persist data; it reads block metadata from DataNodes.

### Dependencies and Integration Points
It integrates with HDDS pipelines, EC replication config, block tokens, xceiver client factory, and container protocol calls. It is selected by `ChecksumHelperFactory` for EC keys.

### Risks and Edge Cases
The node selection assumes stripe checksum placement on replica index 1 and parity nodes. Rebuilding the pipeline as standalone factor-three over a variable node set is specialized behavior that can break if EC pipeline semantics change. Client acquisition must always be released; the current `finally` covers that.

### Test Signals
Tests should verify selected replica indexes, rebuilt pipeline properties, token propagation to `getBlock`, client release on success and failure, and integration with `ECBlockChecksumComputer`.
