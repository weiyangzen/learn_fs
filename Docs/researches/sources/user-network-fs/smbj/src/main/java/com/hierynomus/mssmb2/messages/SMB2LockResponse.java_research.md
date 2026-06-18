<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java` serializes or parses the `SMB2 LockResponse` command body for SMB2 request/response processing. The source was read as a complete 31-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2LockResponse extends SMB2Packet`; methods: `readMessage`; notable imports: `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2LockResponse.java -->
