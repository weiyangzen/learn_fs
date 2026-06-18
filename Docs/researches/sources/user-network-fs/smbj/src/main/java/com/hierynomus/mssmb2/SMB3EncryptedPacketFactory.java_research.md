<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java` handles SMB3 transform framing for encrypted or compressed packets before the normal SMB2 message converter sees the decrypted/decompressed payload. The source was read as a complete 33-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB3EncryptedPacketFactory implements PacketFactory<SMB3EncryptedPacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`.

## Control Flow

`read` wraps raw transport bytes in the corresponding transform packet-data object, while `canHandle` checks the transform protocol id before dispatch.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB3EncryptedPacketFactory.java -->
