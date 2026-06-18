# sources/user-network-fs/samba/source3/torture/nbio.c

## Purpose
`nbio.c` provides older synchronous SMB operation primitives used by generated nbench-style torture scripts. It manages a per-process SMB connection, a local handle table, shared-memory throughput counters, and recursive cleanup helpers.

## Important APIs, types, and functions
The exported API is declared in `proto.h`: `nbio_total`, `nb_alarm`, `nbio_shmem`, `nb_setup`, `nb_unlink`, `nb_createx`, `nb_writex`, `nb_readx`, `nb_close`, `nb_rmdir`, `nb_rename`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_flush`, `nb_deltree`, and `nb_cleanup`. Local state includes `ftable[MAX_FILES]`, global `struct cli_state *c`, `children` shared counters, `buf`, and `nb_start`.

## Control flow
The harness allocates shared memory with `nbio_shmem`, forks clients, calls `nb_setup` per client, and generated script code invokes the operation wrappers. Each wrapper translates a logical handle to an SMB fnum, performs the corresponding `cli_*` call, updates byte counters for reads/writes, and exits on unexpected failures. `nb_alarm` periodically prints aggregate throughput from all children.

## State and persistence behavior
Persistent server-side state consists of files and directories created by the replay. `nb_deltree` recursively lists and removes tree contents, while `nb_cleanup` removes the `clients` directory and marks the child done. Local shared memory tracks bytes, line number, and completion status.

## Dependencies and integration points
The file depends on `torture.c` globals (`line_count`, `nbio_id`) and Samba SMB client APIs. It complements generated load files and the `run_nbench` multiprocess harness in `torture.c`.

## Risks and test signals
Most wrapper failures call `exit(1)`, so this code is intentionally harsh. Handle-table exhaustion, stale logical handles, mismatched read sizes, or cleanup failures are strong test signals. `nb_flush` appears to pass the table index rather than the stored fd, so flush coverage should be interpreted cautiously.
