# sources/user-network-fs/samba/source4/torture/basic/disconnect.c

## Purpose
This file verifies that the server handles abrupt client disconnects while asynchronous requests are outstanding. It targets cleanup paths for pending opens and timed locks.

## Important APIs, types, and functions
Local helpers are `test_disconnect_open()` and `test_disconnect_lock()`, with exported `torture_disconnect()`. Important APIs are `smb_raw_open()`, `smb_raw_open_send()`, `smb_raw_lock()`, `smb_raw_lock_send()`, `smbcli_chkpath()`, `torture_open_connection()`, `talloc_free(cli)`, and `smb_raw_exit()`. It uses `union smb_open`, `union smb_lock`, and `struct smb_lock_entry`.

## Control flow
The harness creates `\test_disconnect`, then for each `torture_numops` iteration sends a blocking/timed lock request behind an existing lock and frees the client before completion. It reconnects, then opens a file, queues two conflicting async opens, validates the connection is still alive with `chkpath`, and frees that client too. Samba3 mode adds a small sleep to reduce process scheduling races.

## State and persistence
The server-side state under test is pending request state, byte-range lock state, and file handle cleanup after transport teardown. Test files are under `\test_disconnect` and are removed by `smbcli_deltree()` at the end.

## Dependencies and integration points
This is a basic torture test using raw SMB open/lock async calls. It relies on talloc ownership: freeing `cli` is the simulated disconnect. The server must tolerate abandoned SMB requests without leaking locks, fnums, or process state.

## Risks
The test intentionally drops connections with live requests, so failures can look like transport instability. Timing is non-deterministic around lock timeouts and Samba3 scheduling. If cleanup does not run after an early return, `\test_disconnect` may remain.

## Test signals
Expected signals are successful `chkpath` before disconnect, no unexpected status from initial open/lock setup, successful reconnection after each forced disconnect, and absence of hangs or later sharing violations caused by leaked locks or opens.
