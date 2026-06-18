<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java` serializes or parses the `SMB2 ChangeNotifyRequest` command body for SMB2 request/response processing. The source was read as a complete 57-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2ChangeNotifyRequest extends SMB2MultiCreditPacket`; state fields: `fileId`, `completionFilter`, `flags`; methods: `writeTo`; notable imports: `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.*`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.smb.SMBBuffer`, `java.util.Set`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyRequest.java -->
