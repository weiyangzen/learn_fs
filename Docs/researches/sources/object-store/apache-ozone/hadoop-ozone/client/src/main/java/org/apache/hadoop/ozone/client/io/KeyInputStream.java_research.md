# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyInputStream.java

Purpose: This read stream composes a key from lazily initialized block input streams and delegates multipart-style offset reads to `MultipartInputStream`.

Important APIs and types: The key factories are `getFromOmKeyInfo` and `getStreamsFromKeyInfo`; runtime overrides are `getNumBytesToRead`, `checkPartBytesRead`, and `getPartStreams`. It uses `OmKeyInfo`, `OmKeyLocationInfo`, `BlockExtendedInputStream`, `BlockInputStreamFactory`, `BlockLocationInfo`, `XceiverClientFactory`, retry functions that refresh OM key info, and `LengthInputStream`.

Control flow: Factory methods extract latest-version block locations, create a `BlockExtendedInputStream` for each location without initializing it, and wrap the resulting `KeyInputStream` with its computed length. If a retry function is supplied, each block stream receives a resolver that refreshes the key and finds a matching block ID. Multipart parts can be split by `partNumber` into separate `LengthInputStream`s. The last block is marked under construction for hsync-created files.

State and persistence behavior: Runtime state is the ordered list of part streams inherited from `MultipartInputStream`. There are no writes; persistence is datanode block reads and possible OM metadata refresh through the retry callback.

Dependencies and integration points: Used by client read APIs and `OzoneInputStream`. It integrates OM key metadata, datanode block input stream factories, hsync metadata (`OzoneConsts.HSYNC_CLIENT_ID`), and multipart part grouping.

Risks: `partsToBlocksMap.values()` does not guarantee sorted part order unless the grouping map ordering happens to match expectations; callers may need deterministic part ordering elsewhere. `checkPartBytesRead` treats any short read as corruption/data loss. Retry block lookup returns null if refreshed key info lacks the same block ID.

Test signals: Tests should verify latest-version filtering, lazy block stream creation, hsync under-construction marking on the last block, retry location refresh, exact short-read exception messages, ByteReaderStrategy sizing, and multipart part grouping correctness.
