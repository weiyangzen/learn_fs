# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairChannelBindings.java

## Purpose
Typed AV pair for MsvAvChannelBindings carrying raw channel-binding bytes.

## Important APIs / Types / Functions
Defines class `AvPairChannelBindings` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairChannelBindings`, `write`, `read`. Source size: 44 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
