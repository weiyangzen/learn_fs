# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacketData.java

## Purpose
Partial SMB packet data holder that reads a header from a backing SMBBuffer before a concrete packet is selected.

## Important APIs / Types / Functions
Defines class `SMBPacketData` in package `com.hierynomus.smb`. Important methods/functions include `SMBPacketData`, `readHeader`, `getHeader`, `getDataBuffer`. Important fields include `header`, `dataBuffer`. Source size: 58 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: header, dataBuffer. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.PacketData, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
