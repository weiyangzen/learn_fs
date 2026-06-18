# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBHeader.java

## Purpose
SMB packet infrastructure type. SMBHeader connects the generic protocol buffer/packet contracts to SMB-specific headers, packet data, and little-endian wire buffers.

## Important APIs / Types / Functions
Defines interface `SMBHeader` in package `com.hierynomus.smb`. Source size: 28 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
