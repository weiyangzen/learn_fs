<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java` writes the FSCTL_PIPE_WAIT request buffer used to wait for a named pipe by UTF-16LE name, optionally with a timeout. The source was read as a complete 80-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FsCtlPipeWaitRequest`; state fields: `timeoutUnit`, `name`, `timeout`, `timeoutSpecified`; methods: `getName`, `getTimeout`, `getTimeoutUnit`, `write`; notable imports: `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `java.util.concurrent.TimeUnit`.

## Control Flow

`write` emits the timeout as 100-nanosecond units when present, writes a timeout-present boolean, reserves padding, writes the UTF-16LE byte length, and appends the pipe name bytes.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.Charsets`, `com.hierynomus.protocol.commons.buffer.Buffer`, `java.util.concurrent.TimeUnit`. It integrates with `SMB2IoctlRequest`/`SMB2IoctlResponse` and named-pipe helper code.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted.

## Test Signals

named-pipe IOCTL round trips against a server plus golden buffer tests for fixed fields and UTF-16 names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipeWaitRequest.java -->
