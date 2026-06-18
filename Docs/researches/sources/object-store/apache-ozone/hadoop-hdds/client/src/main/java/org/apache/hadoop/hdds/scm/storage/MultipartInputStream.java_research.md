# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/MultipartInputStream.java

## Purpose
`MultipartInputStream` concatenates multiple `PartInputStream` instances into one key-level stream. It supports read, seek, skip, available, close, unbuffer, and an optimized positioned-read path when all parts are `StreamBlockInputStream`s.

## Important APIs and Types
The constructor accepts a key name and list of `PartInputStream`s, computes `partOffsets`, total length, and whether the parts are streaming block streams. Key APIs are `readWithStrategy`, `seek`, `readFully(long, ByteBuffer)`, `initialize`, `getPos`, `available`, `skip`, `close`, `getLength`, and testing accessors.

## Control Flow
Reads loop over the current part, delegate bounded strategy reads, and advance `partIndex` when a part is exhausted. `seek` initializes block parts if needed, binary-searches `partOffsets`, resets previous and later parts, and seeks the selected part to the local offset. `readFully` for streaming block parts saves the old position, seeks to the requested position, uses a custom `ByteBufferReader` that invokes `StreamBlockInputStream.readFully`, then restores the old position.

## State and Persistence Behavior
State is in-memory: key, immutable parts list, total length, offsets, closed flag, current/previous part index, and initialized flag. It does not persist data; it coordinates underlying part streams.

## Dependencies and Integration Points
It composes `PartInputStream`, `BlockInputStream`, and `StreamBlockInputStream`, and is used by higher Ozone key input streams to read keys split over multiple blocks/parts.

## Risks
Seek reset behavior can be expensive for many parts and relies on each part's seek implementation being idempotent. The constructor enforces all-streaming type only by checking if the first part is streaming and asserting subsequent parts; mixed lists with first non-streaming do not trigger that assertion. Positioned read support returns false for non-streaming parts, so callers must handle fallback.

## Test Signals
Multipart/key input tests and `TestStreamBlockInputStream` indirectly validate stream-block positioned reads, seek, unbuffer, and close behavior.
