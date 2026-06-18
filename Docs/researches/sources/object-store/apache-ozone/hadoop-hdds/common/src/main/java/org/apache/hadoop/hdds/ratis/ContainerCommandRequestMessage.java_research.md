## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/ContainerCommandRequestMessage.java

Purpose: Ratis `Message` implementation wrapping a `ContainerCommandRequestProto` while separating large write payload bytes from the serialized header.

Important APIs: `toMessage(request, traceId)`, `toProto(bytes, groupId)`, `getContent`, and debug `toString`. Content format is a 4-byte header size, serialized header, then raw data bytes.

Control flow: `toMessage` copies the request, adds trace ID, sets current client version when missing, extracts `WriteChunk.data` or `PutSmallFile.data` into a separate `ByteString`, and clears data from the header. `toProto` reads header length, parses the header, verifies or fills pipeline ID from the Raft group ID, and reattaches data for write/small-file commands. Content is memoized.

State/persistence: immutable header/data fields with memoized serialized content. Dependencies: container protos, Ratis `Message`/`RaftGroupId`, Ozone `ClientVersion`, checksum int encoding, and `HddsUtils` debug redaction.

Integration points: datanode container command replication through Ratis. Risks: malformed byte strings shorter than four bytes or invalid lengths can throw; pipeline/group mismatch is a correctness guard; only WriteChunk and PutSmallFile payloads are split, so new data-bearing commands need updates. Test signals: round trip for write, put small file, and non-data commands; trace/version injection; group ID mismatch; content memoization; malformed length handling; debug redaction.
