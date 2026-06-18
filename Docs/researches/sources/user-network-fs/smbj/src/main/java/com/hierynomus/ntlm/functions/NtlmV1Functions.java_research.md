# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV1Functions.java

## Purpose
Implements NTLMv1 one-way functions for NT and LAN Manager password hashes.

## Important APIs / Types / Functions
Defines class `NtlmV1Functions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmV1Functions`, `NTOWFv1`, `LMOWFv1`. Important fields include `securityProvider`. Source size: 84 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: securityProvider. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.NtlmException, com.hierynomus.security.Cipher, com.hierynomus.security.SecurityException, com.hierynomus.security.SecurityProvider. JDK/JCE dependencies: java.io.UnsupportedEncodingException, java.util.Arrays, java.util.Random.

## Risks and Edge Cases
authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
