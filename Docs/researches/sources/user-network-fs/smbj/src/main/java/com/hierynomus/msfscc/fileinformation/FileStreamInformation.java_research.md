<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java` is a small MS-FSCC file information value object used when SMBJ queries or sets `file StreamInformation` records. The source was read as a complete 43-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileStreamInformation implements FileQueryableInformation`; state fields: `streamList`; methods: `getStreamList`, `getStreamNames`; notable imports: `java.util.ArrayList`, `java.util.List`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `java.util.ArrayList`, `java.util.List`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileStreamInformation.java -->
