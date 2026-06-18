# sources/user-network-fs/samba/source3/torture/mangle_test.c

## Purpose
`mangle_test.c` stress-tests Samba's 8.3 short-name mangling. It creates random long names, queries alternate short names, deletes by short name, recreates by short name, and deletes by long name, while tracking short-name collisions.

## Important APIs, types, and functions
`torture_mangle()` is the exported test. `gen_name()` builds biased random names under `\mangle_test` with common prefixes, extension lengths, and tricky characters. `test_one()` performs the create/query/delete/recreate/delete cycle. A process-local internal TDB maps generated short names to long names to detect collisions.

## Control flow
The test opens one SMB connection, creates a clean `\mangle_test` directory, opens a long-name file with `O_EXCL`, calls `cli_qpathinfo_alt_name`, unlinks via the returned short name, recreates the file via the short-name path, then unlinks via the original long-name path. Every 100 iterations it prints collision and failure statistics.

## State and persistence behavior
The only durable server state is the temporary directory tree and files, removed by `torture_deltree` before and after the run. Local transient state is the internal TDB plus `total`, `collisions`, and `failures` counters.

## Dependencies and integration points
The file uses Samba SMB1 client calls, `torture_open_connection`, `torture_deltree`, TDB utility helpers, and `torture_numops` from `torture.c`. It is registered as the `MANGLE` torture operation through `proto.h` and `torture.c`.

## Risks and test signals
The test intentionally amplifies collision-prone names, so collision reports are diagnostic rather than automatically fatal. Actual failures are inability to unlink/recreate through equivalent short/long names. It is a regression signal for mangling algorithms, case handling, alternate-name lookup, and directory cleanup.
