# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvId.java

## Purpose
Enumerates NTLM target-info AV pair identifiers and their wire values.

## Important APIs / Types / Functions
Defines enum `AvId` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvId`, `getValue`. Important fields include `value`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
