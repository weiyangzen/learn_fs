## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/protocol/DatanodeID.java

Purpose: immutable primary datanode identifier backed by a UUID and cached string/bytes representation.

Important APIs: comparison/equality/hash/toString, JSON-facing `getUuid`, deprecated byte-string accessor, `toPipelineID`, proto conversion, factories from proto/string/UUID, cached `of(UUID)`, and uncached `randomID`.

Control flow: `of(UUID)` uses a concurrent cache to canonicalize identifiers; `randomID()` deliberately avoids adding random IDs to the cache. State/persistence: static concurrent cache grows with distinct UUIDs; instances are immutable.

Dependencies: protobuf `ByteString`, HDDS protobufs, `PipelineID`, `StringWithByteString`. Integration points: `DatanodeDetails`, Ratis peer IDs, pipeline identity conversion, JSON/protobuf serialization. Risks: cache is unbounded; deprecated byte string remains for old proto compatibility; random IDs are not canonicalized. Test signals: cache identity behavior, proto/string round trips, compare ordering, pipeline conversion, and randomID non-cache behavior.
