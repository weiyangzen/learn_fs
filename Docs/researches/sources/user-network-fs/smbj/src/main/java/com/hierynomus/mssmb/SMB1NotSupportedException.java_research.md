<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java` is part of SMBJ's minimal SMB1 negotiation shim, enough to identify/write/read the SMB1 negotiate wrapper before SMB2 takes over. The source was read as a complete 25-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB1NotSupportedException extends TransportException`; notable imports: `com.hierynomus.protocol.transport.TransportException`.

## Control Flow

The class participates in the fixed SMB1 negotiate framing path; most post-negotiation logic deliberately moves to SMB2 packet handling.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.transport.TransportException`. It is used by the transport negotiation path before dialect selection switches to SMB2 packet classes.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

negotiate handshake tests against servers that require SMB1-style dialect advertisement and tests that unsupported SMB1 data is rejected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb/SMB1NotSupportedException.java -->
