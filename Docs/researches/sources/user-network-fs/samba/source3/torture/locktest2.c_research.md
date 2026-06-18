# sources/user-network-fs/samba/source3/torture/locktest2.c

## Purpose
`locktest2.c` is a standalone byte-range lock comparator. It runs randomized lock, unlock, and reopen operations against two SMB shares and corresponding local/NFS paths, then verifies both servers produce identical success/failure behavior.

## Important APIs, types, and functions
`struct record` captures one randomized operation: lock type selector, action selector, connection, file index, filesystem type, range start/length, and whether the record is needed for minimized replay. Core helpers are `try_open`, `try_close`, `try_lock`, `try_unlock`, `connect_one`, `reconnect`, `open_files`, `close_files`, `test_one`, `retest`, and `test_locks`. `main()` parses `-U`, `-s`, `-o`, `-u`, `-a`, `-A`, and `-O`.

## Control flow
The program creates two SMB connections per server and opens two handles per connection for both SMB and NFS/local filesystem paths. It pre-generates `numops` random records, executes each operation against server 0 and server 1, and fails if the boolean result differs. If `-A` analysis mode is active, it repeatedly removes unneeded records to minimize a failing sequence, then replays with verbose lock-table printing through `brl_forall`.

## State and persistence behavior
State is in the `recorded` array, `cli` connection matrix, `fnum` handle matrix, global options, and Samba's readonly locking database access. It creates or reopens `\locktest.dat` on both shares and removes it during cleanup. NFS/local paths are converted from SMB-style backslashes before POSIX `open`/`fcntl`.

## Dependencies and integration points
The binary links against Samba client libraries, loadparm, credentials, `share_mode_lock`/BRL inspection, and POSIX file locking. It is listed separately in `wscript_build`, not just inside `smbtorture3`.

## Risks and test signals
Randomized tests depend on a seed; logs print the seed for reproduction. SMB and NFS lock semantics are not identical in all deployments, so mismatches can be environmental. The minimized replay path is a strong signal for subtle BRL bugs, lock-range overlap errors, reconnect cleanup problems, and oplock interaction when `-O` is enabled.
