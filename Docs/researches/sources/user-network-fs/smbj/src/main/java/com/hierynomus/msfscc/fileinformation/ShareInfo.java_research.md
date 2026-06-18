<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java` parses file-system level information returned by FSCC query-info calls and exposes it as immutable Java accessors. The source was read as a complete 128-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class ShareInfo`; state fields: `totalAllocationUnits`, `callerAvailableAllocationUnits`, `actualAvailableAllocationUnits`, `sectorsPerAllocationUnit`, `bytesPerSector`, `totalSpace`, `callerFreeSpace`, `actualFreeSpace`; methods: `getFreeSpace`, `getCallerFreeSpace`, `getTotalSpace`, `getTotalAllocationUnits`, `getAvailableAllocationUnits`, `getCallerAvailableAllocationUnits`, `getSectorsPerAllocationUnit`, `getBytesPerSector`, `parseFsFullSizeInformation`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`.

## Control Flow

The class is constructor/getter oriented. Control flow lives in `FileInformationFactory`, which reads or writes the corresponding wire fields and returns instances of this type.

## State and Persistence Behavior

State is immutable or effectively immutable value data representing one wire record or control payload. Persistence occurs only on the remote SMB server; this Java object does not cache or store state beyond the current operation.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.protocol.commons.buffer.Buffer.BufferException`. It integrates with `FileInformationFactory`, `FileInformationClass`, `SMB2QueryInfoResponse`, `SMB2QueryDirectoryResponse`, and callers that issue QUERY_INFO or SET_INFO.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly.

## Test Signals

golden-buffer parse and encode tests for the exact MS-FSCC structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fileinformation/ShareInfo.java -->
