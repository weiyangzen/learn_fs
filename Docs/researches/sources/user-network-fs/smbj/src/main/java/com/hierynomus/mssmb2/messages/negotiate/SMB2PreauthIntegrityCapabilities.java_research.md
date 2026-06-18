# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2PreauthIntegrityCapabilities.java

## Purpose
Models the SMB 3.1.1 preauthentication integrity capabilities context, including hash algorithm ids and the negotiate salt.

## Important APIs / Types / Functions
Defines class `SMB2PreauthIntegrityCapabilities` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2PreauthIntegrityCapabilities`, `writeContext`, `readContext`, `getSalt`, `getHashAlgorithms`. Important fields include `DEFAULT_SALT_LENGTH`, `hashAlgorithms`, `salt`. Source size: 87 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: DEFAULT_SALT_LENGTH, hashAlgorithms, salt. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB3HashAlgorithm, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.
