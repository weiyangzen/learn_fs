<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 119-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TransformHeader implements SMBHeader`; state fields: `ENCRYPTED_PROTOCOL_ID`, `headerStartPosition`, `signature`, `nonce`, `originalMessageSize`, `flagsEncryptionAlgorithm`, `sessionId`, `messageEndPosition`; methods: `writeTo`, `readFrom`, `getHeaderStartPosition`, `getMessageEndPosition`, `setMessageEndPosition`, `getSignature`, `setSignature`, `getNonce`, `getOriginalMessageSize`, `getFlagsEncryptionAlgorithm`, `getSessionId`, `isEncrypted`; notable imports: `java.util.Arrays`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`.

## Control Flow

`writeTo` emits the transform header; `readFrom` validates the transform protocol id, records start/end positions, and parses the algorithm/session/nonce or compression fields needed by encryption or decompression layers.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `java.util.Arrays`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2TransformHeader.java -->
