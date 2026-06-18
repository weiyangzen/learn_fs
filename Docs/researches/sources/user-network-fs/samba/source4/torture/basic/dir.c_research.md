# sources/user-network-fs/samba/source4/torture/basic/dir.c

## Purpose
This file provides basic directory listing torture tests. It measures listing behavior over many randomly named files and verifies old SMB list filtering semantics for file and directory attributes.

## Important APIs, types, and functions
The only callback is `list_fn()`, a no-op `smbcli_list*` visitor. Exported tests are `torture_dirtest1()` and `torture_dirtest2()`. They use `smbcli_open()`, `smbcli_close()`, `smbcli_unlink()`, `smbcli_list()`, `smbcli_list_old()`, `smbcli_nt_create_full()`, `smbcli_mkdir()`, `smbcli_deltree()`, `torture_setup_dir()`, and `timeval_current()/timeval_elapsed()`.

## Control flow
`torture_dirtest1()` seeds libc random with zero, creates `torture_numops` files named from hex random values in the share root, runs three wildcard/non-wildcard `smbcli_list()` calls, reports elapsed time, reseeds random, and deletes the same generated names. `torture_dirtest2()` creates `\LISTDIR`, adds `torture_entries` regular files and `torture_entries` directories, then verifies `smbcli_list_old()` counts for all entries, directory-only must-have bits, and archive-file selection.

## State and persistence
The file mutates the test share root and `\LISTDIR`. It depends on deterministic random seeding for cleanup in `dirtest1`. It stores no durable local state.

## Dependencies and integration points
The tests are intended for the basic SMB torture suite and require a connected `smbcli_state`. They depend on Samba's legacy listing API and DOS attribute constants, especially `FILE_ATTRIBUTE_DIRECTORY` and `FILE_ATTRIBUTE_ARCHIVE`.

## Risks
`dirtest1()` creates files in the share root, so cleanup failure leaves scattered hex-named files. `dirtest2()` assumes `.` and `..` are returned by old listing, making it sensitive to server dialect or compatibility behavior. The no-op callback means content correctness is inferred only from counts.

## Test signals
Useful signals are entry-count mismatches, open/mkdir/list failures, incorrect handling of "must have" attribute high bits, and anomalous elapsed-time output under large `torture_numops`.
