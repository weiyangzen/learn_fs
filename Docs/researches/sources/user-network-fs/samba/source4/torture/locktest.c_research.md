# sources/user-network-fs/samba/source4/torture/locktest.c

## Purpose
`locktest.c` is a standalone randomized byte-range lock differential tester. It runs the same generated lock/unlock/reopen sequence against two SMB shares and reports behavioral differences.

## Important APIs, types, and functions
Global knobs include `numops`, `showall`, `analyze`, `hide_unlock_fails`, `use_oplocks`, `lock_range`, `lock_base`, `min_length`, `exact_error_codes`, and `zero_zero`. `struct record` stores one operation. `connect_one()`, `reconnect()`, `open_files()`, `close_files()`, `test_one()`, `retest()`, and `test_locks()` implement connection management, sequence generation, execution, and minimization. `main()` handles popt options, credentials, loadparm, events, gensec, and random seeding.

## Control flow
`main()` parses two UNC paths plus credentials, initializes Samba client state, seeds the random generator, and calls `test_locks()`. `test_locks()` generates `numops` records across two connections and two open file handles per server, opens `\locktest.dat` on both targets, and replays the sequence. On mismatch with `--analyse`, it repeatedly excludes chunks of records to minimize the reproducer, then prints the reduced sequence.

## State and persistence behavior
The program creates and deletes `\locktest.dat` on both target shares. It maintains in-memory connection arrays, file-number arrays, credential objects, and a malloc-backed operation log. Remote byte-range lock state is changed repeatedly and reset by closing/reopening files and reconnecting.

## Dependencies and integration points
It uses Samba client libraries (`smbcli_full_connection`, `smbcli_open`, `smbcli_lock`, `smb_raw_lock`, `smbcli_unlock`, `smbcli_close`, `smbcli_unlink`), command-line credential parsing, loadparm, resolver, event context, and gensec. It is documented by `man/locktest.1.xml`.

## Risks and edge cases
The `use_oplocks` option is parsed but not materially used in the visible lock flow. Large-file capability switches between old lock calls and `RAW_LOCK_LOCKX`. Error comparison normalizes `FILE_LOCK_CONFLICT` to `LOCK_NOT_GRANTED` unless exact errors are requested. `lock_range <= 1` would make random range generation unsafe. Differential failures can reflect timing, server policy, or dialect differences, not just bugs.

## Test signals
Exit code zero means both servers returned equivalent statuses for all generated operations. Nonzero output includes the first mismatch and, with analysis, a minimized operation sequence for reproducing lock semantic differences.
