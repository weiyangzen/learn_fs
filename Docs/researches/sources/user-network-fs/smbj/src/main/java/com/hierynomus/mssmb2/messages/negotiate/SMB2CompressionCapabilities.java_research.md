<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java` models an SMB 3.1.1 negotiate context advertising compression algorithms during dialect negotiation. The source was read as a complete 75-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2CompressionCapabilities extends SMB2NegotiateContext`; state fields: `compressionAlgorithms`; methods: `writeContext`, `readContext`, `getCompressionAlgorithms`; notable imports: `com.hierynomus.mssmb2.SMB3CompressionAlgorithm`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mssmb2.SMB3CompressionAlgorithm`, `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2CompressionCapabilities.java -->
