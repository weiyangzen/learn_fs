# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkKeyHandler.java

Purpose: `ChunkKeyHandler` implements `ozone debug replicas chunk-info`, returning per-datanode chunk location, block metadata, checksums, and EC chunk type for an existing key.

Important APIs and types: It extends `KeyHandler`, uses OM `lookupKey`, `OmKeyInfo`, `OmKeyLocationInfo`, `ContainerOperationClient`, `XceiverClientManager`, `ContainerProtocolCalls.getBlock`, `readContainerFromAllNodes`, `ContainerLayoutVersion`, Jackson streaming `JsonGenerator`, `ECReplicationConfig`, and `ChunkType`.

Control flow: The command resolves the key address, fetches latest key locations, rejects keys with no locations, chooses a read pipeline, reads container metadata from all nodes, gets block data, computes the chunk file path from each datanode's container path and configured layout, emits datanode identity and block/chunk fields, serializes checksum arrays and stripe checksums, and annotates EC replicas as data or parity based on replica index.

State and persistence behavior: It is read-only against OM and datanodes. Output is streamed JSON to stdout; errors for individual datanodes go to stderr and processing continues.

Dependencies and integration points: Registered under `ReplicasDebug`, it links OM key metadata with datanode container storage layout to show the physical chunk file path.

Risks: The acquired `xceiverClient` is tied to a pipeline but the loop intends per-datanode behavior; `getBlock` may not actually retarget for each datanode in the loop. `readContainerResponses.get(datanodeDetails)` can be null. Stripe checksum handling assumes checksum data exists and has at least one checksum. For large keys, output can be large.

Test signals: Tests should cover zero-location keys, Ratis and EC pipelines, data/parity classification, checksum and stripe checksum serialization, missing block response, missing read-container response, and correct file path for file-per-block/file-per-chunk layouts.
