<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java` builds the legacy SMB1 COM_NEGOTIATE request that advertises SMB2 dialect strings to servers that expect negotiation to start with an SMB1-style packet. The source was read as a complete 74-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1ComNegotiateRequest extends SMB1Packet`; state fields: `dialects`; methods: `writeTo`, `read`, `toString`; notable imports: `com.hierynomus.mssmb.SMB1Packet`, `com.hierynomus.mssmb.SMB1PacketData`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

`writeTo` emits SMB1 negotiate parameters and dialect strings; `read` accepts the paired packet data path but performs no response parsing here.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb.SMB1Packet`, `com.hierynomus.mssmb.SMB1PacketData`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/messages/SMB1ComNegotiateRequest.java -->
