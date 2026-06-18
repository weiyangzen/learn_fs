<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java` converts parsed `SMB2PacketData` into concrete SMB2 response packet classes and decides which non-success NTSTATUS values still carry usable response bodies. The source was read as a complete 122-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2MessageConverter`; state fields: `logger`, `FSCTL_PIPE_PEEK`, `FSCTL_PIPE_TRANSCEIVE`, `FSCTL_DFS_GET_REFERRALS`, `FSCTL_SRV_COPYCHUNK`, `FSCTL_SRV_COPYCHUNK_WRITE`; methods: `getPacketInstance`, `readPacket`, `isSuccess`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.mssmb2.messages.*`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacket`, `com.hierynomus.smbj.common.SMBRuntimeException`, `org.slf4j.Logger`, `org.slf4j.LoggerFactory`.

## Control Flow

`readPacket` switches on the SMB2 command to instantiate the response class, then either calls `read` or `readError`. `isSuccess` treats selected warning/status codes as body-bearing success equivalents for session setup, change notify, read/query-info buffer overflow, and specific IOCTL controls.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.mssmb2.messages.*`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBPacket`, `com.hierynomus.smbj.common.SMBRuntimeException`, `org.slf4j.Logger`, `org.slf4j.LoggerFactory`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageConverter.java -->
