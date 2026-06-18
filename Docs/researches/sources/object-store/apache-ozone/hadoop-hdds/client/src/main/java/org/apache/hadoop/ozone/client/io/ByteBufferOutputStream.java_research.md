# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteBufferOutputStream.java

## Purpose
`ByteBufferOutputStream` is the complementary abstract adapter for output streams whose optimized primitive is `write(ByteBuffer, int, int)` but that must also behave like an `OutputStream`.

## Important APIs and Types
It implements `write(byte[])`, `write(byte[], int, int)`, and `write(int)` by wrapping bytes in `ByteBuffer` and delegating to `ByteBufferStreamOutput` methods. Subclasses implement the byte-buffer write method.

## Control Flow
Byte-array writes create heap `ByteBuffer` wrappers over the caller array and pass them through the byte-buffer output path. Single-byte writes allocate a one-byte array.

## State and Persistence Behavior
No state is stored in this abstract class. Output effects are defined by subclasses.

## Dependencies and Integration Points
Implements `ByteBufferStreamOutput`, extends `OutputStream`, and uses Jakarta `@Nonnull` annotations.

## Risks
Wrapping the caller array means subclasses must complete or copy the data before returning if they retain buffers asynchronously. Single-byte writes allocate each call unless subclasses override.

## Test Signals
Indirectly covered by Ozone output classes that inherit this adapter and by byte-buffer write tests.
