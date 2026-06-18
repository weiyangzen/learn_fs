<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java` models FSCTL server-side copy-chunk request or response data used by SMB2 IOCTL copy offload. The source was read as a complete 87-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class CopyChunkRequest`; state fields: `ctlCode`, `resumeKey`, `chunks`, `srcOffset`, `tgtOffset`, `length`; methods: `getCtlCode`, `getResumeKey`, `getChunks`, `write`, `getSrcOffset`, `getTgtOffset`, `getLength`; notable imports: `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`.

## Control Flow

The request writer emits the resume key and one or more chunk descriptors; the response parser reads the three count fields returned by the server after copy offload.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.smb.SMBBuffer`, `java.util.ArrayList`, `java.util.List`. It is passed through SMB2 IOCTL requests for `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced.

## Test Signals

unit tests around accessor values and integration tests through the SMBJ public API path that consumes this type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/copy/CopyChunkRequest.java -->
