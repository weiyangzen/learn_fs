<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 164-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Packet extends SMBPacket<SMB2PacketData, SMB2PacketHeader>`; state fields: `SINGLE_CREDIT_PAYLOAD_SIZE`, `structureSize`, `error`; methods: `getSequenceNumber`, `getStructureSize`, `getBuffer`, `write`, `writeTo`, `read`, `readMessage`, `isSuccess`, `isIntermediateAsyncResponse`, `getMaxPayloadSize`, `getCreditsAssigned`, `setCreditsAssigned`, `getError`, `setError`, `getPacket`, `toString`; notable imports: `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`.

## Control Flow

`write` writes the header followed by subclass body and records message end. `read` binds packet data/header, delegates body parsing to `readMessage`, then jumps to the message end. `readError` follows the same buffer discipline using `SMB2Error`.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`, `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacket`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Packet.java -->
