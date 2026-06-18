<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java` is the central MS-FSCC file-information codec registry. It maps SMB file information POJOs to their `FileInformationClass` values, parses QUERY_INFO and QUERY_DIRECTORY buffers, encodes set-info payloads, and iterates variable-length directory result chains using `NextEntryOffset`. The source was read as a complete 705-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FileInformationFactory`; state fields: `encoders`, `decoders`, `buffer`, `decoder`, `offsetStart`, `next`; methods: `getInformationClass`, `read`, `write`, `getEncoder`, `getDecoder`, `parseFileInformationList`, `createFileInformationIterator`, `hasNext`, `next`, `prepareNext`, `remove`, `parseFileAllInformation`, `parseFileNameInformation`, `parseFileBasicInformation`, `parseFileStandardInformation`, `parseFileInternalInformation`, `parseFileEaInformation`, `parseFileStreamInformation`; notable imports: `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Endian`, `com.hierynomus.smbj.common.SMBRuntimeException`, `java.util.*`.

## Control Flow

Static initialization registers decoder and encoder instances by Java class. Public callers obtain a codec with `getEncoder` or `getDecoder`; parse helpers then read fields in MS-FSCC wire order from a little-endian `Buffer`. Directory listings use `FileInfoIterator`, which seeks to `offsetStart`, decodes one entry, advances by `NextEntryOffset`, and stops when that offset is zero.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.msdtyp.FileTime`, `com.hierynomus.msdtyp.MsDataTypes`, `com.hierynomus.msfscc.FileInformationClass`, `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Endian`, `com.hierynomus.smbj.common.SMBRuntimeException`, `java.util.*`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; UTF-16LE byte counts must remain even and must be counted as bytes on the wire, not Java characters; base-class methods intentionally fail unless subclasses implement the message-specific body.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure; registry lookup coverage for every supported codec and rejection of unsupported classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/FileInformationFactory.java -->
