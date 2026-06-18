<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java

Purpose: Write-path response for EchoRPC benchmarking that intentionally avoids DB/cache mutations.

Important APIs/types/functions: Extends `OMClientResponse`. Constructor stores `OMResponse`. `addToDBBatch` is overridden to return without touching metadata. `@CleanupTableInfo` has no table list.

Control flow and persistence: No persistent state is written. The request can still travel through the write/Ratis/double-buffer path, allowing latency or throughput measurement without backend metadata cost.

Dependencies and integration: Used by EchoRPC write utility or benchmark request handling.

Risks and test signals: It must remain side-effect free; adding DB writes would invalidate benchmark semantics. Tests should verify no table changes, successful response propagation, and Ratis path execution if benchmarked.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/util/OMEchoRPCWriteResponse.java -->
