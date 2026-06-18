# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineID.java

## Purpose
`PipelineID` is the immutable UUID-backed identifier for an SCM pipeline. It supplies conversion helpers for strings, UUIDs, database codecs, and protobuf transport.

## Important APIs and types
`randomId`, `valueOf(UUID)`, and `valueOf(String)` create IDs. `getCodec()` delegates to `UuidCodec` for DB persistence. `getProtobuf()` memoizes a protobuf containing both the legacy string ID and the newer 128-bit UUID form. `getFromProtobuf` prefers `uuid128` and falls back to string `id`.

## Control flow and state
The only state is the final UUID plus a memoized protobuf supplier. Equality and hash code are UUID-only. No persistence side effects occur in this class.

## Dependencies and integration points
It integrates with `HddsProtos.PipelineID`, HDDS DB codec APIs, Jackson's `JsonIgnore`, and Ratis `MemoizedSupplier`. `Pipeline` and pipeline manager code use it as the stable key.

## Risks and test signals
Tests should verify UUID/string/protobuf round trips and legacy protobuf fallback. A protobuf missing both `uuid128` and `id` throws `IllegalArgumentException`, so compatibility tests should keep that failure explicit.
