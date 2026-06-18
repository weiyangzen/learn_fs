<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 56-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2FileId`; state fields: `persistentHandle`, `volatileHandle`; methods: `write`, `read`, `toString`; notable imports: `com.hierynomus.protocol.commons.ByteArrayUtils`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.ByteArrayUtils`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2FileId.java -->
