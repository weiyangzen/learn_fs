# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMSS.cc

## Purpose
Implements the legacy command-based remote/mass-storage-system interface used for directory listing, stat/existence checks, create, unlink, and rename operations through an external RSS/MSS command.

## Important APIs, types, and functions
`XrdOssHandle` wraps a directory stream and flags EOF/type state. `MSS_Opendir()` runs `dlist` and returns a stream-backed handle. `MSS_Readdir()` returns one remote directory entry per stream line and handles EOF/error propagation. `MSS_Closedir()` validates and deletes the handle. `MSS_Create()` invokes `create <path> <mode>`. `MSS_Stat()` either checks existence (`exists` or `statx` for `msscmd`) or parses a `statx` record into `struct stat`; `tranmode()` converts rwx triplets. `MSS_Unlink()` invokes `rm`, and `MSS_Rename()` invokes `mv`. `MSS_Xeq()` is the core executor: it runs `RSSProg`, waits for a response with `RSSTout`, parses the leading return code, logs unexpected failures, and returns a stream to callers that need more data.

## Control flow
All public operations validate path length, issue a command through `MSS_Xeq()`, and return zero or negative errors. Directory open intentionally leaves the command stream alive until readdir/closedir. Stat with a buffer performs command execution, first-line response parsing, stat-field conversion, and stream deletion.

## State and persistence
No file-local persistent state except static `NoResp` throttling timeout logs. External state changes occur in the remote storage service through command execution. Directory handles own subprocess streams and must be closed.

## Dependencies and integration points
Depends on `XrdOucProg`/`XrdOucStream`, `RSSProg`, `RSSCmd`, `RSSTout`, `isMSSC`, global logging/tracing, and config-stage setup in `XrdOssConfig.cc`. Called by create, rename, stat, unlink, and directory operations in the wider OSS implementation.

## Risks and test signals
The command protocol is brittle: first response line must be numeric and statx formatting must match `sscanf`. Timeout behavior maps no response to custom OSS errors. Tests should use fake RSS programs for success, ENOENT-ok cases, malformed replies, delayed replies, statx directories/links/files, long paths, and handle misuse.
