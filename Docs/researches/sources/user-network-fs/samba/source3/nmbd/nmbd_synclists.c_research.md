# sources/user-network-fs/samba/source3/nmbd/nmbd_synclists.c

## Purpose
`nmbd_synclists.c` implements asynchronous browse-list synchronization with remote browse servers. It forks children that connect over SMB/NBT, enumerate remote browse lists, write temporary results, and later merges completed rows into the unicast subnet.

## Important APIs, types, and functions
- `sync_browse_lists` starts one asynchronous sync operation.
- `sync_check_completion` detects finished child processes and merges results.
- `sync_child` performs SMB connection, anonymous IPC$ setup, and NetServerEnum calls.
- `complete_sync` parses child output; `complete_one` updates workgroups or servers.
- `callback` writes NetServerEnum rows.

## Control flow
The parent skips self IPs, allocates a sync record, creates a lock-directory file name, links it into `syncs`, forks, and returns. The child connects using forced NBT transport, negotiates SMB, enumerates domains and optionally servers, writes rows, and exits. Completion checks parse output rows, update/create unicast workgroups and servers with max TTL, delete the file, and free the record.

## State and persistence behavior
Runtime state is the `syncs` linked list plus temporary `sync.N` files in the lock directory. Merge results mutate the unicast subnet's workgroup/server lists. Temp files are deleted after completion.

## Dependencies and integration points
This code integrates with Samba client APIs, workgroup/server-list APIs, lock-directory configuration, process helpers, token parsing, and string utilities.

## Risks and edge cases
Forked children isolate blocking SMB calls but need correct cleanup. The global `fp` assumes process isolation. Result parsing depends on callback formatting. Modern servers may reject SMB1/anonymous IPC$. PID-existence checks can theoretically race with pid reuse.

## Test signals
Test child-output parsing, server/workgroup merge behavior, self-IP skip, failed connection cleanup, and stale sync file handling. Integration tests need a controllable SMB browse server.
