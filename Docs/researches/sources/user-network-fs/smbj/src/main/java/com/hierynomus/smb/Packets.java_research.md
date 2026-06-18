# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/Packets.java

## Purpose
Extracts serialized SMB packet bytes from a packet's SMBBuffer using header start and message end positions while preserving the original read cursor.

## Important APIs / Types / Functions
Defines class `Packets` in package `com.hierynomus.smb`. Important methods/functions include `getPacketBytes`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smbj.common.SMBRuntimeException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
