# sources/user-network-fs/samba/source3/utils/net_serverid.c

## Purpose
Implements `net serverid`, primarily `wipedbs`, for cleaning stale smbXsrv session, tree-connect, open, and replay records owned by dead server IDs. Also implements `exists` for server ID liveness checks.

## Important APIs, Types, and Functions
Cleanup state is stored in `struct wipedbs_state`, `struct wipedbs_server_data`, and `struct wipedbs_record_marker`. Traversal callbacks collect session/tcon/open/replay records. Temporary `dbwrap_rbt` databases index server IDs and open/replay records. Deletion uses `dbwrap_do_locked()` plus value comparison in `wipedbs_delete_fn()` and `smbXsrv_replay_cleanup()` for open replay state.

## Control Flow
`net_serverid_wipedbs()` opens temporary indexes, traverses smbXsrv global databases, checks all collected server IDs with `serverid_exists()`, deletes records for non-existing servers, and then removes orphan replay records. Disconnected durable opens are only candidates after their timeout expires. `--test` performs a dry run, and `--verbose` prints detailed decisions.

## State and Persistence
Reads and may delete records from Samba runtime TDBs. It copies keys/values during scan and revalidates under lock before deletion, limiting races with active servers.

## Dependencies and Integration Points
Depends on server ID helpers, `dbwrap`, smbXsrv session/tcon/open traversal, NDR open-record decoding, durable replay cleanup, and is reused by `net tdb smbXsrv wipedbs`.

## Risks
Destructive cleanup can remove live state if liveness or timeout logic is wrong. The temporary RBT traversal order is assumed stable when applying batched liveness results. Malformed open blobs and record changes need careful handling.

## Test Signals
Use fixtures with live/dead IDs, disconnected opens below/above timeout, changed records between scan/delete, malformed open records, orphan replay records, dry-run mode, verbose output, and `exists` present/absent results.
