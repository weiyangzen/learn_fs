# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBBuffer.java

## Purpose
SMB-specific little-endian Buffer specialization with reserved-byte writers and UTF-16 string length helpers.

## Important APIs / Types / Functions
Defines class `SMBBuffer` in package `com.hierynomus.smb`. Important methods/functions include `SMBBuffer`, `putReserved`, `putReserved1`, `putReserved2`, `putReserved4`, `putString`, `putStringLengthUInt16`. Important fields include `RESERVED_2`, `RESERVED_4`. Source size: 101 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: RESERVED_2, RESERVED_4. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian. JDK/JCE dependencies: java.util.Arrays.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
