# sources/user-network-fs/samba/source4/torture/local/dbspeed.c

## Purpose
`dbspeed.c` benchmarks and sanity-checks TDB and LDB lookup performance for SID/UID-style records in local smbtorture tests.

## Important APIs, types, and functions
`tdb_add_record()` inserts string key/value pairs. `test_tdb_speed()` creates `test.tdb`, inserts SID-to-UID and UID-to-SID records, repeatedly fetches random pairs, and stores global `tdb_speed`. `ldb_add_record()` inserts one SID DN with a UID attribute. `test_ldb_speed()` creates `test.ldb`, adds an index, inserts records, performs base and indexed subtree searches, checks talloc block counts, and reports speed relative to TDB. `torture_local_dbspeed()` registers both tests.

## Control flow
The TDB test runs first and sets `tdb_speed`. The LDB test then computes its own rate and prints the LDB/TDB ratio. Both use `torture_entries` and `torture:timelimit` to control dataset size and duration.

## State and persistence behavior
The tests create local `test.tdb` and `test.ldb` files in the current directory and unlink them on success or failure. The only cross-test state is the global `tdb_speed`.

## Dependencies and integration points
The file depends on tdb, ldb, `ldb_wrap_connect`, `tdb_wrap_open`, loadparm TDB flags, and smbtorture local suite registration.

## Risks and edge cases
The LDB ratio assumes the TDB test ran first. Performance results depend on filesystem, random seed, `torture_entries`, and `timelimit`. The talloc block-count leak heuristic is coarse and can break if LDB internals change allocation behavior.

## Test signals
Passing tests show records can be inserted and fetched through TDB and LDB, UID indexing works for subtree searches, and no obvious allocation growth occurs during add/search loops.
