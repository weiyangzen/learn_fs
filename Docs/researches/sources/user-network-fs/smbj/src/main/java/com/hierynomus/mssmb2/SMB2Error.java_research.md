<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java` supports SMB2/SMB3 protocol encoding in package `com.hierynomus.mssmb2`. The source was read as a complete 176-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMB2Error`; state fields: `errorData`, `absolute`, `unparsedPathLength`, `substituteName`, `printName`, `requiredBufferLength`; methods: `readErrorContext`, `readErrorData`, `getErrorData`, `read`, `readOffsettedString`, `isAbsolute`, `getUnparsedPathLength`, `getSubstituteName`, `getPrintName`, `getRequiredBufferLength`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Error.java -->
