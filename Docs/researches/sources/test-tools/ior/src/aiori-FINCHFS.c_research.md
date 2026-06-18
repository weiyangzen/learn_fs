# sources/test-tools/ior/src/aiori-FINCHFS.c

## Purpose
Implements a thin IOR backend for FINCHFS with transfer, metadata, rename, fsync, version, and mdtest support.

## Important APIs, Types, and Functions
- `struct FINCHFS_File` wraps an integer FINCHFS descriptor.
- `struct finchfs_option` contains `chunk_size`; `FINCHFS_options` calls `finchfs_set_chunk_size` when nonzero.
- `FINCHFS_initialize` and `FINCHFS_finalize` call `finchfs_init(NULL)` and `finchfs_term()`.
- File operations wrap `finchfs_create`, `finchfs_open`, `finchfs_pwrite`, `finchfs_pread`, `finchfs_close`, `finchfs_unlink`, and `finchfs_fsync`.
- Metadata operations wrap `finchfs_mkdir`, `finchfs_rename`, `finchfs_rmdir`, and `finchfs_stat`; statfs is a stub success path.

## Control Flow
The backend mirrors CHFS: dry-run returns success without backend calls, create/open allocate a descriptor wrapper, transfers return backend byte counts, close frees the wrapper, and sync is a no-op.

## State and Persistence
Persistent data lives in FINCHFS. Runtime state is a global hints pointer and per-file descriptor wrapper. Durability is available through `finchfs_fsync`; there is no global sync implementation.

## Dependencies and Integration Points
Requires `<finchfs.h>` and IOR callback integration. `enable_mdtest = true`; rename support is registered, unlike CHFS.

## Risks and Edge Cases
- Statfs reports success without filling fields.
- Transfer short counts are not retried locally.
- `chunk_size` is declared as an option flag despite being a size.
- `FINCHFS_access` ignores the requested access mode and only stats the path.

## Test Signals
Validate create/open/xfer/close/delete, rename, dry-run behavior, chunk-size option, fsync behavior, and mdtest metadata paths.
