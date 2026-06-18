<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java` serializes or parses the `SMB2 SessionSetup` command body for SMB2 request/response processing. The source was read as a complete 149-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2SessionSetup extends SMB2Packet`; state fields: `negotiatedDialect`, `securityMode`, `clientCapabilities`, `securityBuffer`, `previousSessionId`, `sessionFlags`, `value`; methods: `writeTo`, `readMessage`, `readSecurityBuffer`, `putFlags`, `getSessionFlags`, `setSessionFlags`, `setPreviousSessionId`, `setSecurityBuffer`, `getSecurityBuffer`, `getValue`; notable imports: `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`, `java.util.Set`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

`readMessage` validates or skips the fixed structure header, reads offsets and lengths, seeks to variable buffers when present, and exposes parsed fields through getters.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `static com.hierynomus.protocol.commons.EnumWithValue.EnumUtils.toEnumSet`, `java.util.Set`, `com.hierynomus.mssmb2.SMB2Dialect`, `com.hierynomus.mssmb2.SMB2GlobalCapability`, `com.hierynomus.mssmb2.SMB2MessageCommandCode`, `com.hierynomus.mssmb2.SMB2Packet`, `com.hierynomus.mssmb2.SMB2PacketHeader`, `com.hierynomus.protocol.commons.EnumWithValue`. It integrates with `SMB2PacketHeader`, `SMB2MessageCommandCode`, `SMB2MessageConverter`, and session/tree/share/file abstractions that create or consume this message.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

golden SMB2 request/response buffers for the command structure size, offsets, and payload lengths; integration coverage through session setup, tree connect, create/read/write/query/close workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/SMB2SessionSetup.java -->
