# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPair.java

## Purpose
Abstract base for typed NTLM target-info AV pairs with common id/value storage and read/write contracts.

## Important APIs / Types / Functions
Defines class `AvPair` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPair`, `read`, `getValue`, `toString`. Important fields include `avId`, `value`. Source size: 54 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: avId, value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
