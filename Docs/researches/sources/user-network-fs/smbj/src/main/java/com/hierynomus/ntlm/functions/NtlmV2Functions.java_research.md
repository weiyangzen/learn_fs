# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV2Functions.java

## Purpose
Implements NTLMv2 response-key, LMv2 response, NT proof string, NT response blob, session base key, and KXKEY derivation.

## Important APIs / Types / Functions
Defines class `NtlmV2Functions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmV2Functions`, `computeResponse`, `NTOWFv2`, `LMOWFv2`, `getLmV2Response`, `getNtV2Response`, `getSessionBaseKey`, `ntResponseTemp`, `ntProofStr`, `kxKey`. Important fields include `random`, `securityProvider`. Source size: 214 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: random, securityProvider. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.NtlmChallenge, com.hierynomus.ntlm.messages.TargetInfo, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian, com.hierynomus.security.SecurityProvider. JDK/JCE dependencies: java.util.Random. External dependencies: org.bouncycastle.util.Arrays.

## Risks and Edge Cases
authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
