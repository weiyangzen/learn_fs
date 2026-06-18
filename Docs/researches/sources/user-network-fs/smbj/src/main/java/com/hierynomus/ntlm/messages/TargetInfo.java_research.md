# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/TargetInfo.java

## Purpose
Mutable collection of NTLM AV pairs with read-until-EOL parsing, write-with-EOL serialization, copy, get, put, and existence helpers.

## Important APIs / Types / Functions
Defines class `TargetInfo` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `TargetInfo`, `readFrom`, `writeTo`, `copy`, `getAvPair`, `putAvPair`, `hasAvPair`, `toString`. Important fields include `logger`, `targetInfo`. Source size: 99 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: logger, targetInfo. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.av.AvId, com.hierynomus.ntlm.av.AvPair, com.hierynomus.ntlm.av.AvPairEnd, com.hierynomus.ntlm.av.AvPairFactory, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
