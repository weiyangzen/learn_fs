# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairString.java

## Purpose
Typed AV pair for UTF-16LE string-valued target-info fields such as NetBIOS and DNS names.

## Important APIs / Types / Functions
Defines class `AvPairString` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairString`, `read`, `write`. Source size: 45 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
