<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java` models FSCTL server-side copy-chunk request or response data used by SMB2 IOCTL copy offload. The source was read as a complete 55-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class CopyChunkResponse`; state fields: `chunksWritten`, `chunkBytesWritten`, `totalBytesWritten`; methods: `getChunksWritten`, `getChunkBytesWritten`, `getTotalBytesWritten`, `read`; notable imports: `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`.

## Control Flow

The request writer emits the resume key and one or more chunk descriptors; the response parser reads the three count fields returned by the server after copy offload.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.buffer.Buffer`, `com.hierynomus.smb.SMBBuffer`. It is passed through SMB2 IOCTL requests for `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkResponse.java -->
