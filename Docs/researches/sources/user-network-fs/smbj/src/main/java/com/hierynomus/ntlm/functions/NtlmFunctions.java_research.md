# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmFunctions.java

## Purpose
Central NTLM helper library for Unicode/OEM encoding, MD4/MD5/HMACT64 hashing, RC4 encryption, and DES key setup.

## Important APIs / Types / Functions
Defines class `NtlmFunctions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmFunctions`, `unicode`, `oem`, `md4`, `hmac_md5`, `md5`, `rc4k`, `setupKey`, `getDESCipher`. Important fields include `UNICODE`. Source size: 168 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: UNICODE. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Cipher.CryptMode.ENCRYPT, com.hierynomus.ntlm.NtlmException, com.hierynomus.protocol.commons.Charsets, com.hierynomus.security.Cipher, com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, ... . JDK/JCE dependencies: java.nio.charset.Charset.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
