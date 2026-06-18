# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Endian.java

## Purpose
Defines big-endian and little-endian primitive/string codecs used by Buffer and SMBBuffer.

## Important APIs / Types / Functions
Defines class `to` in package `com.hierynomus.protocol.commons.buffer`. Important methods/functions include `readNullTerminatedUtf16String`, `readUtf16String`, `writeNullTerminatedUtf16String`, `writeUInt16`, `readUInt16`, `writeUInt24`, `readUInt24`, `writeUInt32`, `readUInt32`, `writeUInt64`, `readUInt64`, `writeLong`. Important fields include `NULL_TERMINATOR`, `LE`, `BE`. Source size: 322 lines.

## Control Flow
Control flow is cursor based: read methods check availability and advance rpos, write methods ensure capacity and advance wpos, endian helpers implement primitive byte order, and string helpers select UTF-16/UTF-8 behavior from Charset names.

## State and Persistence
State fields observed: NULL_TERMINATOR, LE, BE. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets. JDK/JCE dependencies: java.io.ByteArrayOutputStream, java.nio.charset.Charset.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Exercise endian read/write values, boundary underflow, capacity growth, string encodings, null-terminated strings, and InputStream behavior.
