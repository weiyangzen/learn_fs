<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 274-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketHeader implements SMBHeader`; state fields: `EMPTY_SIGNATURE`, `STRUCTURE_SIZE`, `SIGNATURE_OFFSET`, `SIGNATURE_SIZE`, `PROTOCOL_ID`, `dialect`, `creditCharge`, `creditRequest`, `creditResponse`, `message`, `messageId`, `asyncId`, `sessionId`, `treeId`, `statusCode`, `flags`; methods: `writeTo`, `writeChannelSequenceReserved`, `writeCreditRequest`, `writeCreditCharge`, `setMessageId`, `setMessageType`, `getMessage`, `getTreeId`, `setTreeId`, `getSessionId`, `setSessionId`, `setDialect`, `isFlagSet`, `setFlag`, `getMessageId`, `setCreditRequest`, `getCreditRequest`, `getCreditResponse`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `java.util.Arrays`.

## Control Flow

`writeTo` writes the 64-byte SMB2 header and chooses async-id versus tree-id layout from flags. `readFrom` validates the protocol id, captures status, command, credits, flags, ids, signature, and derives message end from compounding offset or packet size.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`, `com.hierynomus.smbj.common.Check`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `java.util.Arrays`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketHeader.java -->
