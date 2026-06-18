<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java` serializes or parses the `SMB2 TreeConnectResponse` command body for SMB2 request/response processing. The source was read as a complete 101-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2TreeConnectResponse extends SMB2Packet`; state fields: `shareType`, `shareFlags`, `capabilities`, `maximalAccess`; methods: `readMessage`, `setShareType`, `isDiskShare`, `isNamedPipe`, `isPrinterShare`, `getShareFlags`, `setShareFlags`, `getCapabilities`, `setCapabilities`, `getMaximalAccess`; notable imports: `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2ShareCapabilities`, `com.hierynomus.mssmb2.SMB2ShareFlags`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2ShareCapabilities`, `com.hierynomus.mssmb2.SMB2ShareFlags`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponse.java -->
