<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 94-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketData extends SMBPacketData<SMB2PacketHeader>`; methods: `getSequenceNumber`, `isSuccess`, `isIntermediateAsyncResponse`, `isOplockBreakNotification`, `isCompounded`, `next`, `isDecrypted`, `toString`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacketData`, `static com.hierynomus.mssmb2.SMB2MessageCommandCode.SMB2_OPLOCK_BREAK`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`.

## Control Flow

Construction reads an SMB2 header from the buffer. Helpers classify success, pending async responses, oplock break notifications, and compounded packets; `next` reuses the same buffer at the next compounded message.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBPacketData`, `static com.hierynomus.mssmb2.SMB2MessageCommandCode.SMB2_OPLOCK_BREAK`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.isSet`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketData.java -->
