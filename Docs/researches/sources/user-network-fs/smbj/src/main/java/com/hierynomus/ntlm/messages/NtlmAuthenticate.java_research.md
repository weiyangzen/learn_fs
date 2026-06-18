# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmAuthenticate.java

## Purpose
Serializes NTLM AUTHENTICATE_MESSAGE fields, offsets, optional version, optional MIC, and payload byte arrays.

## Important APIs / Types / Functions
Defines class `NtlmAuthenticate` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmAuthenticate`, `getBaseMessageSize`, `write`, `setMic`, `getVersion`, `toString`. Important fields include `lmResponse`, `ntResponse`, `userName`, `domainName`, `workstation`, `encryptedRandomSessionKey`, `mic`. Source size: 139 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: lmResponse, ntResponse, userName, domainName, workstation, encryptedRandomSessionKey, mic. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.functions.NtlmFunctions, com.hierynomus.protocol.commons.ByteArrayUtils, com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian, ... . JDK/JCE dependencies: java.util.Set.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
