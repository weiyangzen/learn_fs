<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java` parses the FSCTL_PIPE_PEEK response for named pipes, including pipe state, queued byte counts, message counts, and trailing payload data. The source was read as a complete 87-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public class FsCtlPipePeekResponse`; state fields: `STRUCTURE_SIZE`, `state`, `readDataAvailable`, `numberOfMessages`, `messageLength`, `data`, `value`; methods: `getState`, `getReadDataAvailable`, `getNumberOfMessages`, `getMessageLength`, `getData`, `read`, `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`.

## Control Flow

`read` consumes fixed fields in order, maps the numeric pipe state through `EnumWithValue`, then reads the remaining bytes as peeked pipe data.

## State and Persistence Behavior

State is in-memory and per packet: parsed headers, offsets, ids, flags, payload lengths, and byte arrays are retained only for the life of the SMB request/response object. No file-backed persistence is performed here.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`, `com.hierynomus.protocol.commons.buffer.Buffer`. It integrates with `SMB2IoctlRequest`/`SMB2IoctlResponse` and named-pipe helper code.

## Risks and Edge Cases

wire field order, signedness, and little-endian widths must match MS-SMB2/MS-FSCC exactly; large server-provided lengths can allocate or copy more data than expected unless upstream bounds are enforced; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

named-pipe IOCTL round trips against a server plus golden buffer tests for fixed fields and UTF-16 names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/msfscc/fsctl/FsCtlPipePeekResponse.java -->
