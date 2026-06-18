# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2query.c

Implements server-side TRANS2 query handlers for path, file, and filesystem information.

Key points:
- Shared `query` emits responses for `SMB_QUERY_FILE_BASIC_INFO`, `ALL_INFO`, `STANDARD_INFO`, and `EA_INFO`.
- Path queries resolve `t->serv->path + path` and call `dirstat`.
- File queries resolve an FID, use `dirfstat` for open file descriptors, or `dirstat` for path-only file state.
- Filesystem queries support allocation, volume, size, and attribute information levels with mostly synthetic values.

Dependencies:
- Uses `SmbTree`, `SmbFile`, Plan 9 `Dir`, SMB buffer serialization, DOS attribute conversion, and time conversion helpers.

Notable behavior:
- `SMB_QUERY_FILE_STREAM_INFO` is intentionally unsupported.
- Several fields are placeholders, such as serial `0xdeadbeef`, hard link count, and free space values.
