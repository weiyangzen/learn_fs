# sources/test-tools/ior/src/aiori-RADOS.c

## Purpose
Implements an IOR backend for Ceph RADOS objects. It maps IOR file names to RADOS object ids and provides object create/open, read/write, delete, size, and existence checks.

## Important APIs, Types, and Functions
- `RADOS_options_t` stores Ceph user, config file, and pool.
- Global `rados_cluster` and `rados_ioctx` represent the cluster connection and pool I/O context.
- `RADOS_check_params` requires user, conf, and pool.
- `RADOS_Initialize` creates/configures/connects the cluster and creates the pool ioctx.
- `RADOS_Create_Or_Open` duplicates the object id and optionally issues a create write op with exclusive or idempotent semantics.
- `RADOS_Xfer` uses librados write and read ops for positional object I/O.
- `RADOS_GetFileSize` stats an object with a read op; `RADOS_Access` uses stat to check existence.

## Control Flow
Initialization must precede file operations. Create/open returns a heap-allocated object id string as the handle. Close frees the object id. Delete issues a remove write operation. Fsync is a no-op because writes complete through librados operations.

## State and Persistence
Persistent state is in Ceph RADOS objects. Runtime state is global cluster/ioctx plus per-handle object id strings. There is no directory hierarchy or POSIX statfs/stat support.

## Dependencies and Integration Points
Requires `<rados/librados.h>`, IOR utilities, and Ceph configuration. Registered callbacks include unsupported mdtest-like metadata functions, but `enable_mdtest` is not set.

## Risks and Edge Cases
- Object names are raw test file names; path-like names are not directories.
- `RADOS_Access` uses bitwise `|` instead of logical `||` when checking errors.
- Read error reporting passes `ret` to `RADOS_ERR` even when `read_ret` or byte-count mismatch is the failing condition.
- Statfs, mkdir, rmdir, and stat are unsupported and always warn/fail.
- No dry-run path.

## Test Signals
Test missing option validation, cluster/pool connect failures, create exclusive vs idempotent behavior, positional reads/writes, size/existence checks, delete, unsupported metadata responses, and object names containing slashes.
