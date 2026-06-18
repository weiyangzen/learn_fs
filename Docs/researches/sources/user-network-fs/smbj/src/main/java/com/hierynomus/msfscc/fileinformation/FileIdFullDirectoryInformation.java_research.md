<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java` models one variable-length MS-FSCC directory enumeration entry returned by SMB2 QUERY_DIRECTORY. The source was read as a complete 81-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileIdFullDirectoryInformation extends FileDirectoryQueryableInformation`; state fields: `creationTime`, `lastAccessTime`, `lastWriteTime`, `changeTime`, `endOfFile`, `allocationSize`, `fileAttributes`, `eaSize`, `fileId`; methods: `getCreationTime`, `getLastAccessTime`, `getLastWriteTime`, `getChangeTime`, `getEndOfFile`, `getAllocationSize`, `getFileAttributes`, `getEaSize`, `getFileId`; notable imports: `com.hierynomus.msdtyp.FileTime`.

## Control Flow

The object is produced while walking a QUERY_DIRECTORY response chain. Its inherited `nextOffset` tells the iterator where the next record begins, while `fileName` and typed metadata describe the current entry.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; multi-entry QUERY_DIRECTORY buffers with nonzero and zero `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileIdFullDirectoryInformation.java -->
