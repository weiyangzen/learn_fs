<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 32-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2PacketFactory implements PacketFactory<SMB2PacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2PacketFactory.java -->
