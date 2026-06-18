# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmMessage.java

## Purpose
Base class for NTLM messages that normalizes caller-provided flags with mandatory NTLM and Unicode defaults.

## Important APIs / Types / Functions
Defines class `NtlmMessage` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmMessage`. Important fields include `DEFAULT_FLAGS`, `negotiateFlags`, `version`. Source size: 36 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: DEFAULT_FLAGS, negotiateFlags, version. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.NtlmNegotiateFlag.*. JDK/JCE dependencies: java.util.EnumSet, java.util.Set.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
