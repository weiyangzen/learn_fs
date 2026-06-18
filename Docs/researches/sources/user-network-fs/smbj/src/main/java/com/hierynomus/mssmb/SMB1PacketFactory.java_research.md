<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 33-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1PacketFactory implements PacketFactory<SMB1PacketData>`; methods: `read`, `canHandle`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`.

## Control Flow

`read` wraps incoming bytes in `SMB1PacketData`; `canHandle` recognizes SMB1 by its protocol header bytes.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.transport.PacketFactory`, `java.io.IOException`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1PacketFactory.java -->
