<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java` serializes or parses the `SMB2 Close` command body for SMB2 request/response processing. The source was read as a complete 103-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Close extends SMB2Packet`; state fields: `fileId`, `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `allocationSize`, `size`, `fileAttributes`; methods: `writeTo`, `readMessage`, `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getAllocationSize`, `getSize`, `getFileAttributes`, `setFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

`writeTo` emits the fixed SMB2 structure size and command-specific fields in specification order, using buffer offset placeholders where variable payloads follow the fixed body.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2FileId`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2Close.java -->
