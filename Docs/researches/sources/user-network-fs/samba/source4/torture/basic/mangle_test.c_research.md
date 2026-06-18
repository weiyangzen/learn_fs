# sources/user-network-fs/samba/source4/torture/basic/mangle_test.c

## Purpose
This file stress-tests 8.3 short-name mangling. It creates randomized long names, queries their alternate names, verifies open/unlink interoperability through long and short names, and tracks short-name collisions.

## Important APIs, types, and functions
Key functions are `test_one()`, `gen_name()`, and exported `torture_mangle()`. It uses an internal TDB (`tdb_open(NULL, ..., TDB_INTERNAL, ...)`) with `tdb_fetch_bystring()` and `tdb_store_bystring()` to remember short-name mappings. SMB APIs include `smbcli_open()`, `smbcli_close()`, `smbcli_qpathinfo_alt_name()`, `smbcli_unlink()`, `smbcli_unlink_wcard()`, and `smbcli_rmdir()`.

## Control flow
`torture_mangle()` opens the in-memory TDB, creates `\mangle_test`, then runs `torture_numops` generated filenames. For each name, `test_one()` creates the long name, queries the server alternate name, deletes via the short name, recreates via short name, deletes via long name, and records or reports alternate-name collisions. Periodic progress prints collision and failure ratios.

## State and persistence
Server state is confined to `\mangle_test`, which is wildcard-unlinked and removed. Process-global counters `total`, `collisions`, and `failures`, plus global `tdb`, persist across the test invocation. The TDB is in-memory only.

## Dependencies and integration points
The test depends on `system/dir.h`, TDB utility helpers, Samba pathinfo alternate-name support, and torture settings. It is part of the basic SMB torture tests and assumes the target filesystem exposes short names.

## Risks
Short-name behavior is configuration- and filesystem-dependent; valid failures may indicate disabled mangling rather than a generic SMB bug. The random generator intentionally biases toward collision-prone names, which can be expensive for large `torture_numops`. Global counters are not reset inside `torture_mangle()`, so repeated in-process calls may accumulate totals.

## Test signals
Failures are inability to query alternate names, inability to unlink/recreate across long/short names, or a nonzero `failures` counter. Collisions are reported but not necessarily fatal unless they lead to operation failures.
