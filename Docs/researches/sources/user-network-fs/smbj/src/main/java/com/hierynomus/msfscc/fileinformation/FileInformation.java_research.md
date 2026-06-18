<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java` defines a marker or codec contract for MS-FSCC file information records used by SMB2 query and set-info paths. The source was read as a complete 36-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public interface FileInformation`; notable imports: `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

There is no runtime branch logic; implementors are selected by `FileInformationFactory` and then encoded into or decoded from SMB buffers.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformation.java -->
