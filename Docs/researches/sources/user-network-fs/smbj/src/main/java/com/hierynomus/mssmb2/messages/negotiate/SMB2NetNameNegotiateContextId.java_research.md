# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NetNameNegotiateContextId.java

## Purpose
Models the SMB2 netname negotiate context with a UTF-16 null-terminated server name payload.

## Important APIs / Types / Functions
Defines class `SMB2NetNameNegotiateContextId` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NetNameNegotiateContextId`, `writeContext`, `readContext`, `getNetName`. Important fields include `netName`. Source size: 52 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: netName. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.
