# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacket.java

## Purpose
SMB packet infrastructure type. SMBPacket connects the generic protocol buffer/packet contracts to SMB-specific headers, packet data, and little-endian wire buffers.

## Important APIs / Types / Functions
Defines class `SMBPacket` in package `com.hierynomus.smb`. Important methods/functions include `SMBPacket`, `getHeader`, `read`, `getBuffer`. Important fields include `header`, `buffer`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: header, buffer. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
