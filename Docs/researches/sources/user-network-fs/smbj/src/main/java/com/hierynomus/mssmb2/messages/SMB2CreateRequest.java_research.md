<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java` serializes or parses the `SMB2 CreateRequest` command body for SMB2 request/response processing. The source was read as a complete 102-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CreateRequest extends SMB2Packet`; state fields: `fileAttributes`, `shareAccess`, `createDisposition`, `createOptions`, `path`, `accessMask`, `impersonationLevel`; methods: `writeTo`, `getCreateDisposition`; notable imports: `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.ensureNotNull`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.AccessMask`, `com.hierynomus.msfscc.FileAttributes`, `com.hierynomus.mssmb2.*`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smbj.common.SmbPath`, `java.util.Set`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.ensureNotNull`, `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toLong`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2CreateRequest.java -->
