<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 46-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2DecryptedPacketData extends SMB2PacketData`; methods: `next`, `isDecrypted`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2DecryptedPacketData.java -->
