# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/utils/ClientCommandsUtils.java

## Purpose
Utility for interpreting optional read-chunk-version fields on container protocol requests.

## Important APIs and types
Two overloads of `getReadChunkVersion` accept `ReadChunkRequestProto` and `GetSmallFileRequestProto`. Both return the explicitly set version or default to `ReadChunkVersion.V0`.

## Control flow and state
The class is stateless and non-instantiable. Its only branch preserves backward compatibility for requests created before the read-chunk-version field existed.

## Dependencies and integration points
Used by response builders and datanode/client read paths to decide whether to return single-buffer V0 data or V1 data buffers.

## Risks and test signals
Tests should verify absent-field fallback and explicit V1 handling for both request types. Changing the default would break old clients.
