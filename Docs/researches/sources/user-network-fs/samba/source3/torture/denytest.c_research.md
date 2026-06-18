# sources/user-network-fs/samba/source3/torture/denytest.c

## Purpose
`denytest.c` validates classic SMB1 open deny-mode semantics. It runs large expected-result matrices for combinations of access mode, deny mode, executable/non-executable file name, and one-connection versus two-connection opens, then checks whether a second handle can be opened, read, and written.

## Important APIs, types, and functions
The central data type is `enum deny_result` (`A_X`, `A_0`, `A_R`, `A_W`, `A_RW`) describing first-open failure, second-open failure, or read/write capability. `denytable1[]` and `denytable2[]` encode expected results. `torture_denytest1()` tests two opens on one `cli_state`; `torture_denytest2()` tests two separate `cli_state` connections. Helper functions `denystr`, `openstr`, `resultstr`, and `progress_bar` make output readable.

## Control flow
Each test opens a torture connection, creates two files (`.dat` and `.exe`), and iterates the table. For each row it opens the first handle with `mode1/deny1`, opens the second handle with `mode2/deny2`, then if both succeed attempts a one-byte `cli_read` and `cli_writeall` through the second handle. The observed aggregate result is compared to the table, and mismatches are printed unless `torture_showall` requests all rows.

## State and persistence behavior
The test temporarily creates `\denytest1.dat`, `\denytest1.exe`, `\denytest2.dat`, and `\denytest2.exe`, writes their names into them, opens and closes many SMB handles, then unlinks the files. No durable state is intended after cleanup.

## Dependencies and integration points
The file is part of the `smbtorture3` binary and is declared in `torture/proto.h`. It depends on `torture_open_connection`, `torture_close_connection`, `cli_openx`, `cli_read`, `cli_writeall`, `cli_close`, and `cli_unlink`.

## Risks and test signals
Deny-mode behavior is legacy and protocol-sensitive; expected outcomes differ for same-session versus cross-session opens and for DOS executable handling. The table is the main oracle, so changes must be deliberate. Failures indicate regressions in share-mode conflict resolution, DOS deny-mode mapping, or read/write access enforcement.
