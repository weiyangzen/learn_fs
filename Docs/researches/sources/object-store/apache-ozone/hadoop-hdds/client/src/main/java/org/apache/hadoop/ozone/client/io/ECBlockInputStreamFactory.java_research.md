# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactory.java

## Purpose
`ECBlockInputStreamFactory` abstracts creation of EC block readers, selecting between direct EC reads and reconstruction reads based on location availability.

## Important APIs and Types
It declares `create(boolean missingLocations, List<DatanodeDetails> failedLocations, ReplicationConfig, BlockLocationInfo, XceiverClientFactory, Function<BlockID, BlockLocationInfo>, OzoneClientConfig)`, returning `BlockExtendedInputStream`.

## Control Flow
Implementations inspect `missingLocations`: false creates a direct `ECBlockInputStream`; true creates a reconstruction wrapper around `ECBlockReconstructedStripeInputStream`, seeding known failed datanodes.

## State and Persistence Behavior
The interface has no state or persistence behavior.

## Dependencies and Integration Points
Used by `ECBlockInputStreamProxy`, with `ECBlockInputStreamFactoryImpl` as the implementation.

## Risks
The boolean controls a major behavior difference. Incorrectly passing false with missing locations can cause direct read failures; incorrectly passing true increases CPU and read overhead through reconstruction.

## Test Signals
`TestECBlockInputStreamProxy` and EC factory utility tests validate direct versus reconstruction selection.
