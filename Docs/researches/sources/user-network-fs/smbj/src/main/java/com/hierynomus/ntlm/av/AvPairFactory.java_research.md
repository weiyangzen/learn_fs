# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFactory.java

## Purpose
Dispatches NTLM target-info AV pair parsing by reading the AvId field and constructing the matching AvPair subtype.

## Important APIs / Types / Functions
Defines class `AvPairFactory` in package `com.hierynomus.ntlm.av`. Important methods/functions include `read`. Source size: 54 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException, com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
