# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ExtendedInputStream.java

## Purpose
`ExtendedInputStream` is the shared base class for Ozone input streams that need `InputStream`, Hadoop `Seekable`, `CanUnbuffer`, `ByteBufferReadable`, and `StreamCapabilities` behavior.

## Important APIs and Types
It implements `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `read(ByteReaderStrategy)`, default `seek`, default `seekToNewSource`, `hasCapability`, and a default unsupported positioned `readFully(long, ByteBuffer)`. Subclasses implement `readWithStrategy(ByteReaderStrategy)`.

## Control Flow
Standard read overloads are converted into `ByteArrayReader` or `ByteBufferReader`, then delegated to subclass traversal logic. Single-byte read uses a one-byte array and unsigned conversion. Capabilities advertise byte-buffer read and unbuffer support.

## State and Persistence Behavior
The base class has no mutable stream state beyond inherited `InputStream` behavior. It persists nothing.

## Dependencies and Integration Points
Base class for `BlockExtendedInputStream` descendants, `MultipartInputStream`, EC stream wrappers, and other Ozone read abstractions. It uses Hadoop stream capability constants and Apache Commons `NotImplementedException`.

## Risks
Default `seek` throws `NotImplementedException`, so subclasses must override it if they expose seekable behavior. `readFully` default returns false rather than throwing, so callers must check the boolean to know positioned reads are unsupported.

## Test Signals
Covered indirectly by every subclass read test, including block, multipart, streaming, and EC tests.
