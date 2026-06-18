# sources/test-tools/ior/src/aiori-CHFS.c

## Purpose
Implements a thin IOR backend for CHFS with file, transfer, fsync, directory, stat, and mdtest callbacks.

## Important APIs, Types, and Functions
- `struct CHFS_File` wraps an integer CHFS file descriptor.
- `struct chfs_option` currently exposes `chfs.chunk_size`; `CHFS_options` optionally calls `chfs_set_chunk_size`.
- `CHFS_initialize`/`CHFS_finalize` call `chfs_init(NULL)` and `chfs_term()`.
- `CHFS_create`, `CHFS_open`, `CHFS_xfer`, `CHFS_close`, `CHFS_delete`, and `CHFS_fsync` directly wrap the corresponding `chfs_*` APIs.
- Metadata wrappers include `chfs_stat`, `chfs_mkdir`, and `chfs_rmdir`; `CHFS_statfs` returns success without filling statfs fields.

## Control Flow
IOR installs hints, initializes CHFS, then creates/opens files unless `hints->dryRun` is set. Transfers use `chfs_pwrite` for writes and `chfs_pread` otherwise, returning the backend byte count rather than forcing the requested length.

## State and Persistence
The backend state is a global `hints` pointer plus per-open `struct CHFS_File` allocations. Durability is through `chfs_fsync`; `CHFS_sync` is a no-op.

## Dependencies and Integration Points
Requires `<chfs.h>` plus IOR `ior_aiori_t` integration. `enable_mdtest = true`, so metadata functions must behave correctly for mdtest-style workloads.

## Risks and Edge Cases
- Dry-run create/open returns `NULL`, and close/delete/fsync become no-ops.
- Transfer short counts are returned to the caller without local retry logic.
- `CHFS_statfs` does not populate capacity fields, so consumers expecting real filesystem statistics get zeros or prior contents.
- Option help marks `chunk_size` as a flag even though it is a size value.

## Test Signals
Compile with CHFS headers, validate chunk-size option parsing, verify dry-run does not call CHFS APIs, test short transfer reporting, and run mdtest-style mkdir/rmdir/stat/access paths.
