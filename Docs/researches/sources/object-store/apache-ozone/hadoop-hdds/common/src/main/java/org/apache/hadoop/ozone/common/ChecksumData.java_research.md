# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumData.java

## Purpose
`ChecksumData` is an immutable Java wrapper around the container protobuf `ChecksumData` message. It stores checksum type, bytes per checksum, and ordered checksum bytes, and provides conversion, equality, hashing, string formatting, and mismatch verification.

## Important APIs, types, and functions
- Constructors accept checksum type and bytes-per-checksum, with optional checksum list.
- Accessors: `getChecksumType`, `getBytesPerChecksum`, and `getChecksums`.
- `getProtoBufMessage()` lazily builds and memoizes the protobuf via `MemoizedSupplier`.
- `getFromProtoBuf(ContainerProtos.ChecksumData)` converts protobuf to wrapper.
- `verifyChecksumDataMatches(int thisStartIndex, ChecksumData that)` compares this object's checksums from a start index against another computed checksum set.
- `equals`, `hashCode`, and `toString` implement value semantics and hex rendering.

## Control flow
Construction validates non-null type, wraps the checksum list with `Collections.unmodifiableList`, and sets up a memoized protobuf supplier. Verification first checks that the compared checksum count fits from the requested start index, then compares each checksum and throws `OzoneChecksumException` with detailed context on count or byte mismatch.

## State and persistence behavior
The wrapper is annotated immutable and stores final fields. The checksum list is unmodifiable but not defensively copied, so external mutation of the original list before or after construction can affect immutability if the source list is mutable. The protobuf representation is memoized in memory and is the serialized form used in container metadata.

## Dependencies and integration points
It depends on container protobufs, `ChecksumType`, Ratis `ByteString`, HDDS `StringUtils`, Apache Commons `HashCodeBuilder`, JCIP `@Immutable`, and Ratis `MemoizedSupplier`. It is produced by `Checksum` and consumed by verification and container/chunk metadata code.

## Risks and edge cases
- Lack of defensive copy weakens the immutability guarantee.
- `verifyChecksumDataMatches` assumes `thisStartIndex` is valid; negative values can lead to index errors rather than a clean checksum exception.
- `hashCode` converts the list to an array, which is fine for typical checksum counts but can cost memory for very large lists.
- `toString` renders all checksums in hex, which may be verbose and could expose checksum material in logs.

## Test signals
Tests should cover proto round-trip, memoized protobuf stability, equality/hash code, unmodifiable checksum list behavior, mutation of source list after construction, successful and failed verification at different start indexes, negative/out-of-range start indexes, and `toString` formatting for empty and non-empty checksum lists.
