# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/ByteBufferInputStream.java

## Purpose
Adapts a `ByteBuffer` to a read-only `InputStream`.

## Important APIs, Types, And Functions
Constructor stores `buffer.asReadOnlyBuffer()`. Overrides `read()` and `read(byte[], int, int)`. Package-visible `assertArrayIndex` validates array bounds and overflow.

## Control Flow
Single-byte read returns `-1` at EOF or the next unsigned byte. Bulk read validates arguments, returns `0` for zero-length reads, returns `-1` if no remaining bytes, then copies the minimum of requested and remaining bytes.

## State And Persistence
State is the read-only duplicate buffer and its position. The original buffer position is unaffected. No persistence.

## Dependencies And Integration Points
Useful anywhere APIs require `InputStream` over in-memory `ByteBuffer` content.

## Risks
No `mark/reset` support beyond `InputStream` defaults. It is not synchronized. The constructor does not null-check explicitly, so null produces `NullPointerException`.

## Test Signals
Tests should cover single and bulk reads, EOF, zero-length reads, invalid bounds, overflow bounds, read-only behavior, and original-position independence.
