# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingSource.java

Purpose: source-side mapping interface for directory streaming.

Important APIs and types: `getFilesToStream(String id)` returns a map from logical stream names to real local file paths and may throw `InterruptedException`.

Control flow and state: none in the interface.

Dependencies and integration: implemented by `DirectoryServerSource` and consumed by `DirstreamServerHandler`.

Risks and test signals: map ordering affects stream order, and implementations must choose how to handle unsafe IDs. Tests should cover empty maps, deterministic order where required, interruption propagation, and invalid ID handling.
