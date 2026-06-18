<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java` implements SMB2 packet framing, header handling, packet-data parsing, or multi-credit payload accounting for the core SMBJ transport. The source was read as a complete 35-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2MultiCreditPacket extends SMB2Packet`; state fields: `maxPayloadSize`; methods: `getMaxPayloadSize`, `getPayloadSize`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

round-trip packet header tests, compounded packet tests, signing/encryption/compression framing tests, and NTSTATUS error-body tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MultiCreditPacket.java -->
