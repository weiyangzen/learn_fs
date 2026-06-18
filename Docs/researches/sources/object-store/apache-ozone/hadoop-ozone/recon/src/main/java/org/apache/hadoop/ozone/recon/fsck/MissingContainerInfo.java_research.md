## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/MissingContainerInfo.java

Purpose: API payload DTO describing one missing container for missing-container responses.

Important APIs/types/functions: constructor and getters for `containerId`, `missingSinceTimestamp`, `lastKnownPipelineId`, `lastKnownDatanodes`, and `keysInContainer`.

Control flow: none beyond object construction. State is immutable by absence of setters, but contained lists are not defensively copied.

State and persistence: no persistence; it represents data assembled from health tables, pipeline/datanode history, and key metadata. Dependency on `KeyMetadata` connects missing-container output to Recon namespace metadata.

Risks: external mutation of list references can alter response contents. Tests should validate JSON serialization shape, empty key/datanode lists, and null pipeline/list handling expected by API clients.
