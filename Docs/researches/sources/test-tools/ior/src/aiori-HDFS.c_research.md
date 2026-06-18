# sources/test-tools/ior/src/aiori-HDFS.c

## Purpose
Implements the IOR `HDFS` backend using libhdfs. It manages a per-options HDFS filesystem connection, file create/open/read/write/flush/close/delete, and metadata callbacks.

## Important APIs, Types, and Functions
- `hdfs_options_t` stores user, name node, replication count, direct-I/O flag, block size, runtime `hdfsFS`, and name-node port.
- `HDFS_options` initializes defaults from `$USER` and `"default"` name node.
- `hdfs_connect` builds a new forced HDFS client instance and stores it in `o->fs`.
- `HDFS_Create_Or_Open` maps IOR flags to libhdfs flags, coordinates shared-file truncation with MPI barriers, and calls `hdfsOpenFile`.
- `HDFS_Xfer` loops over `hdfsWrite` or `hdfsPread`, retries short transfers, and flushes writes with `hdfsHFlush` at the end.
- `HDFS_Fsync` uses `hdfsHSync`; metadata uses `hdfsCreateDirectory`, `hdfsDelete`, `hdfsExists`, `hdfsGetPathInfo`, and capacity APIs.

## Control Flow
Every metadata and file path first ensures the HDFS connection exists. Shared-file write create/open lets rank 0 truncate, then uses MPI barriers so other ranks open afterward. Writes use stream-positioned `hdfsWrite`; reads use positional `hdfsPread`. Close closes only the file handle; disconnect is implemented but not registered in `ior_aiori_t`.

## State and Persistence
Persistent state is in HDFS. Runtime connection state is stored in the allocated module options, not a global. Durability/visibility comes from `hdfsHFlush` after writes and `hdfsHSync` during fsync.

## Dependencies and Integration Points
Requires libhdfs, MPI barriers, IOR hints, and POSIX flag constants. It registers mdtest-capable metadata operations but no initialize/finalize callbacks.

## Risks and Edge Cases
- The connection is not finalized through the `ior_aiori_t`, so `hdfs_disconnect` may not be called by normal backend lifecycle.
- `IOR_RDWR` is unsupported and fatal.
- Direct I/O depends on `O_DIRECT` availability and may only affect client-side flags.
- `HDFS_GetFileSize` declares MPI aggregation variables but returns only the local `hdfsGetPathInfo` size.
- `HDFS_stat` maps HDFS permissions directly into `st_mode` without file-type bits.

## Test Signals
Test default/user/name-node options, shared-file truncation barriers, file-per-process writes, short read/write retry behavior, flush/fsync visibility, metadata callbacks, direct-I/O flag handling, and cleanup of HDFS client connections in long-running processes.
