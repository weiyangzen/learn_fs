# sources/user-network-fs/samba/source4/cluster/local.c

## Purpose
Provides the default local/non-cluster backend for the cluster abstraction.

## Important APIs, types, and functions
- `local_id()` builds a `server_id` with caller-supplied `pid` and `task_id`, `NONCLUSTER_VNN`, and `SERVERID_UNIQUE_ID_NOT_TO_VERIFY`.
- `local_db_tmp_open()` builds a `.tdb` name under `smbd_tmp_path()`, computes configured hash size and TDB flags, and opens it with `dbwrap_local_open()`.
- `local_backend_handle()` returns `NULL`.
- `local_message_init()` succeeds without doing work.
- `local_message_send()` returns `NT_STATUS_INVALID_DEVICE_REQUEST`.
- `cluster_local_init()` installs `cluster_local_ops`.

## Control flow
The backend is a static `cluster_ops` table. Public calls from `cluster.c` land on these functions when no cluster backend overrides them.

## State and persistence behavior
There is no private backend state. Temporary DBs are real local TDB files under Samba's tmp path, opened with mode `0600`. Local messaging send is not supported by this backend.

## Dependencies and integration points
Uses dbwrap, system file flags, loadparm helpers, `smbd_tmp_path()`, and generated server ID constants. It is built into the private `cluster` library by `wscript_build`.

## Risks and edge cases
- `local_db_tmp_open()` allocates `dbname` on `mem_ctx` rather than `tmp_ctx`, so the constructed name lives longer than the path-building temporary context.
- Local message init returning success while send is unsupported can hide missing backend support until a send is attempted.
- The comment says “server a server_id”, a documentation typo only.

## Test signals
Tests should verify tmp DB path/flags integration, server ID fields, and that local messaging send fails predictably.
