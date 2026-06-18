# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDiscardPreallocatedBlocks.java

## Purpose
`TestDiscardPreallocatedBlocks` verifies that when a container is closed after only part of a preallocated key has been written, the client discards the unused preallocated block in the closed container and allocates a fresh block for subsequent writes.

## Important APIs, types, and functions
This abstract non-HA test uses `TestHelper.createKey` and `waitForContainerClose`, `KeyOutputStream`, `BlockOutputStreamEntry`, `OmKeyLocationInfo`, `ContainerInfo`, `Pipeline`, and SCM container/pipeline managers. It reads block size from `OZONE_SCM_BLOCK_SIZE` and uses fixed-length test data from `ContainerTestHelper`.

## Control flow
The test creates a RATIS key with expected size `2 * blockSize`, causing two stream entries to be preallocated. It writes exactly one block, snapshots the original location info and stream entries, resolves the first block's container and pipeline, and asserts the pipeline has three datanodes. It then closes the current container through `waitForContainerClose`, writes another block, and verifies there are now three stream entries.

The key assertion is that the first block ID is unchanged, while the second current location's block ID differs from the originally preallocated second stream entry. This proves the unused preallocated block was discarded and replaced.

## State and persistence behavior
The test inspects client-side preallocation state and SCM-backed location information. It does not read the final key data; instead it focuses on block identity and stream-entry mutation after container closure.

## Dependencies and integration points
Integration spans the non-HA cluster fixture, Ozone client preallocation, SCM container/pipeline lookup, container close handling, and key-output stream location management.

## Risks and test signals
The test assumes factor-three RATIS pipeline size of three and that the first write consumes exactly the first preallocated block. Its strongest signal is block ID replacement for the unused second preallocation while preserving the first committed block ID.
