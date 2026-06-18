# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/StreamingDestination.java

Purpose: destination-side mapping interface for directory streaming.

Important APIs and types: `mapToDestination(String name)` returns the local `Path` where the logical streamed file name should be written.

Control flow and state: none in the interface.

Dependencies and integration: implemented by `DirectoryServerDestination` and called by `DirstreamClientHandler` before creating output files.

Risks and test signals: implementations define security boundaries for streamed filenames. Tests should check path normalization, parent existence creation, and rejection or handling of unsafe logical names in concrete implementations.
