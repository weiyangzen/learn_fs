# sources/test-tools/ior/src/aiori-DFS.c

## Purpose
Implements the IOR `DFS` backend for DAOS DFS, including pool/container connection, DFS mount, file/object transfer, metadata operations, statfs, rename, and optional container destruction.

## Important APIs, Types, and Functions
- `DFS_options_t` contains pool, DAOS system group, container label, chunk size, file and directory object classes, prefix, and destroy-on-finalize.
- Global handles `poh`, `coh`, and `dfs` represent DAOS pool, container, and DFS mount state.
- `HandleDistribute` broadcasts pool/container/DFS global handles from rank 0 to the rest of `testComm`.
- `parse_filename` splits object basename and parent directory path, resolving relative directory paths with `realpath`.
- `lookup_insert_dir` caches opened DFS directory handles in a `d_hash_table`.
- `DFS_Create`, `DFS_Open`, `share_file_handle`, and `DFS_Xfer` wrap `dfs_open`, global file-handle sharing, `dfs_write`, and `dfs_read`.
- Metadata operations use `dfs_remove`, `dfs_mkdir`, `dfs_move`, `dfs_access`, `dfs_stat`, and DAOS pool space queries.

## Control Flow
`DFS_check_params` validates pool/container and initializes `testComm` if needed. `DFS_Init` is reference-counted with `dfs_init_count`: the first initialization calls `daos_init`, resolves object-class names, creates a directory-handle cache, connects or creates the container on rank 0, mounts DFS, distributes global handles, and applies a DFS prefix. Later initializations only refresh mutable object-class options. File create/open is done on all ranks for file-per-process or on rank 0 for shared-file mode, then shared through a DAOS global object handle. Finalization waits at MPI barriers, releases cached directory handles, unmounts DFS, closes or destroys the container, disconnects the pool, and calls `daos_fini`.

## State and Persistence
The DAOS container stores all persistent data. Runtime state is global and process-wide: pool/container/mount handles, object classes, cached directory object handles, and init count. `DFS_Fsync` and `DFS_Sync` call `dfs_sync`; comments note DFS has no client cache in this context.

## Dependencies and Integration Points
Requires DAOS, DFS, GURT hash/list utilities, MPI, and IOR utility macros. Integration includes IOR transfer hints, `testComm`, `rank`, mdtest callbacks, and `get_version` returning `"DAOS"`.

## Risks and Edge Cases
- Error macros jump to an `out` label, so each function's local cleanup path is central to correctness.
- `parse_filename` uses `realpath` for relative parent directories, which fails if the parent path does not exist locally even though DFS paths may not be local POSIX paths.
- Directory-handle cache uses `D_HASH_FT_NOLOCK`; thread safety depends on IOR calling patterns.
- `DFS_Open` sets `mode = S_IFREG | flags`, which mixes open flags into a mode variable.
- Shared file handles rely on correct rank-0 object creation/opening and MPI broadcasts.
- Finalization resets option fields, which may surprise code reusing the options object after finalize.

## Test Signals
Run DAOS DFS tests for existing and missing containers, destroy-on-finalize, object-class names, prefix use, file-per-process vs shared-file handle distribution, mkdir/rename/rmdir/stat/access, statfs pool-space reporting, and repeated initialize/finalize cycles.
