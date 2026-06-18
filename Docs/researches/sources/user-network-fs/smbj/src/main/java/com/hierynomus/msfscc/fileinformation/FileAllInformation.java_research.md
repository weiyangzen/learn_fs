<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java` is an aggregate MS-FSCC `FileAllInformation` value object combining basic, standard, internal, EA, access, position, mode, alignment, and name data from a single query-info response. The source was read as a complete 76-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileAllInformation implements FileQueryableInformation`; state fields: `basicInformation`, `standardInformation`, `internalInformation`, `eaInformation`, `accessInformation`, `positionInformation`, `modeInformation`, `alignmentInformation`, `nameInformation`; methods: `getBasicInformation`, `getStandardInformation`, `getInternalInformation`, `getEaInformation`, `getAccessInformation`, `getPositionInformation`, `getModeInformation`, `getAlignmentInformation`, `getNameInformation`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileAllInformation.java -->
