# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/RandomAccessFileChannel.java

## Purpose
Owns a read-only `RandomAccessFile` and `FileChannel` with synchronized open, seek, read-fill, and close helpers.

## Important APIs, Types, And Functions
Public methods are `isOpen`, `open(File)`, `position(long)`, `read(ByteBuffer)`, and `close`. Fields track the file, `RandomAccessFile`, and channel.

## Control Flow
`open()` asserts no current file, opens the file in `"r"` mode, and stores channel state. `position()` seeks only when the requested position differs. `read()` loops until the target buffer is full or EOF returns false. `close()` clears `blockFile`, closes channel and RAF independently, logs close failures, and nulls fields.

## State And Persistence
State is the currently open file/channel and position in the OS file handle. The class does not mutate file contents.

## Dependencies And Integration Points
Depends on Java IO/NIO, Ratis `Preconditions`, and SLF4J. Used where block/chunk readers need positioned full-buffer reads.

## Risks
All methods synchronize on the object, so concurrent reads serialize. `isOpen()` is based on `blockFile`, not channel state. `read()` can spin if a custom channel returns zero while the buffer remains writable, though file channels normally progress or EOF.

## Test Signals
`TestRandomAccessFileChannel` covers open/close, positioning, full and partial reads, EOF, and internal cleanup. Additional tests can inject close exceptions and concurrent access.
