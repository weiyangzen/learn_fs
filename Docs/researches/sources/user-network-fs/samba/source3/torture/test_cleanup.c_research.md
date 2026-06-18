# sources/user-network-fs/samba/source3/torture/test_cleanup.c

Purpose: This file tests that smbd correctly cleans up server-side share modes and byte-range locks when a connection is forcibly killed. The three exported tests are regression cases around stale lock records causing later opens or writes to behave incorrectly.

Important APIs/types/functions: `run_cleanup1()` checks share-mode cleanup after `smbXcli_conn_samba_suicide()`. `run_cleanup2()` checks byte-range lock cleanup after killing one lock holder. `run_cleanup4()` checks an iteration bug where cleanup of one stale share mode must not skip conflict detection against another live open. Core APIs are `torture_open_connection()`, `cli_openx()`, `cli_ntcreate()`, `cli_lock32()`, `cli_smbwrite()`, `cli_close()`, and `smbXcli_conn_samba_suicide()`.

Control flow: Each test opens one or more SMB connections, creates/open files with specific share and access modes, then kills one smbd-backed connection using the Samba-specific suicide helper. After the kill, a second connection probes whether a new open or write sees the expected post-cleanup state. `run_cleanup2()` also verifies the file is initially locked by expecting `NT_STATUS_FILE_LOCK_CONFLICT` before the kill, sleeps briefly to allow process death, and then expects the write to succeed.

State/persistence behavior: State lives primarily in smbd's locking databases: share-mode records, byte-range lock records, and open file handles. Test files `\cleanup1`, `\cleanup2`, and `\cleanup4` are created on the remote share. Cleanup is server-driven, not local; the point is to prove dead process records are removed while live records remain enforced.

Dependencies and integration points: The tests use Samba torture connection helpers, SMB client calls, low-level locking headers, SMBX client suicide support, and generated open-files NDR definitions. They integrate with the source3 torture suite as individual `run_cleanup*` entrypoints.

Risks: These tests are intentionally Samba-specific because they use `smbXcli_conn_samba_suicide()`. Timing can be fragile around process death; `run_cleanup2()` hard-codes a one-second sleep. Misconfiguration of durable handles, clustering, or nonstandard lock backends can alter cleanup timing.

Test signals: Expected statuses are precise: second open in cleanup1 must succeed, pre-kill write in cleanup2 must return `NT_STATUS_FILE_LOCK_CONFLICT`, post-kill write must succeed, and cleanup4's final conflicting open must return `NT_STATUS_SHARING_VIOLATION`.
