<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1Header implements SMBHeader`; state fields: `headerStartPosition`, `messageEndPosition`; methods: `writeTo`, `readFrom`, `getHeaderStartPosition`, `getMessageEndPosition`, `setMessageEndPosition`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `com.hierynomus.smb.SMBHeader`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1Header.java -->
