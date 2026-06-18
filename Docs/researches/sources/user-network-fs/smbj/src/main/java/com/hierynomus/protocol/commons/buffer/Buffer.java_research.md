# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Buffer.java

## Purpose
Generic mutable read/write byte buffer with endian-aware primitive, string, null-terminated string, skip, compact, and InputStream helpers.

## Important APIs / Types / Functions
Defines class `Buffer` in package `com.hierynomus.protocol.commons.buffer`. Important methods/functions include `BufferException`, `PlainBuffer`, `getNextPowerOf2`, `Buffer`, `array`, `available`, `clear`, `rpos`, `wpos`, `ensureAvailable`, `ensureCapacity`, `compact`. Important fields include `logger`, `DEFAULT_SIZE`, `MAX_SIZE`, `data`, `endianness`, `rpos`, `wpos`. Source size: 792 lines.

## Control Flow
Control flow is cursor based: read methods check availability and advance rpos, write methods ensure capacity and advance wpos, endian helpers implement primitive byte order, and string helpers select UTF-16/UTF-8 behavior from Charset names.

## State and Persistence
State fields observed: logger, DEFAULT_SIZE, MAX_SIZE, data, endianness, rpos, wpos. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.ByteArrayUtils. JDK/JCE dependencies: java.io.ByteArrayOutputStream, java.io.IOException, java.io.InputStream, java.nio.charset.Charset, java.nio.charset.UnsupportedCharsetException. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Exercise endian read/write values, boundary underflow, capacity growth, string encodings, null-terminated strings, and InputStream behavior.
