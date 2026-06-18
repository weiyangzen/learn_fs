<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java` wraps SMB protocol failures with the failed command and NTSTATUS code so higher SMBJ APIs can expose protocol errors consistently. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class SMBApiException extends SMBRuntimeException`; state fields: `failedCommand`, `statusCode`; methods: `getStatus`, `getStatusCode`, `getFailedCommand`, `getMessage`; notable imports: `com.hierynomus.mserref.NtStatus`, `com.hierynomus.smbj.common.SMBRuntimeException`.

## Control Flow

Control flow is limited to simple buffer helpers and accessors; higher-level SMB session/tree/file code orchestrates when this type is used.

## State and Persistence Behavior

The class owns no durable state; it carries transient protocol data for the surrounding SMBJ connection workflow.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.mserref.NtStatus`, `com.hierynomus.smbj.common.SMBRuntimeException`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMBApiException.java -->
