# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2EncryptionCapabilities.java

## Purpose
Represents the SMB 3 encryption capabilities negotiate context. It serializes a non-empty ordered list of SMB3EncryptionCipher ids and parses the server's advertised cipher list back into enum values.

## Important APIs / Types / Functions
Defines class `SMB2EncryptionCapabilities` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2EncryptionCapabilities`, `writeContext`, `readContext`, `getCipherList`. Important fields include `cipherList`. Source size: 69 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: cipherList. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB3EncryptionCipher, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.
