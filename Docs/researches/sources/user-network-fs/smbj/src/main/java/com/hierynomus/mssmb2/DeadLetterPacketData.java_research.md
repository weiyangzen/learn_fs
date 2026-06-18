<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 28-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class DeadLetterPacketData extends SMBPacketData<SMBHeader>`; notable imports: `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smb.SMBPacketData`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smb.SMBPacketData`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/DeadLetterPacketData.java -->
