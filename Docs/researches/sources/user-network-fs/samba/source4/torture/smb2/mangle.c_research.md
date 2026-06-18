# sources/user-network-fs/samba/source4/torture/smb2/mangle.c

## Purpose
`mangle.c` tests SMB2 8.3 short-name/name-mangling behavior. It stress-generates long names, verifies that short aliases can open and delete the same file, tracks short-name collisions, and checks that SMB2 FIND can use a mangled search mask.

## Important APIs, Types, and Functions
`test_one()` creates a file, queries its alternate short name with `smb2_qpathinfo_alt_name()`, unlinks via the short name, recreates via the short name, unlinks via the long name, and stores short-name-to-long-name mappings in an internal TDB. `gen_name()` produces randomized names under `mangle_test\\` with biased prefixes/extensions to provoke mangling collisions. `torture_smb2_mangle()` drives `torture_numops` iterations and reports collision/failure counts. `test_mangled_mask()` creates `verylongfilename`, obtains its short name from `SMB2_FIND_BOTH_DIRECTORY_INFO`, then uses that short name as a single-entry find pattern. `torture_smb2_name_mangling_init()` registers `mangle` and `mangled-mask`.

## Control Flow
The stress test creates the test directory, repeatedly generates a candidate name, and runs the create/query-shortname/delete/recreate/delete cycle. The TDB is used only to notice whether two distinct long names mapped to the same short alias. The mask test refreshes a directory handle before enumerating so the new file is visible, skips dot entries, captures the returned short name, and performs a single-result find with that pattern.

## State and Persistence Behavior
Server-side test files are transient under `mangle_test`. Client-side collision tracking uses an in-memory `TDB_INTERNAL` database and static counters `total`, `collisions`, and `failures`. The file does not persist data beyond the test process.

## Dependencies and Integration Points
The test depends on SMB2 create/close/find/pathinfo/unlink helpers, TDB utility wrappers, random name generation from the C runtime, and torture settings such as `torture_numops` and `progress`.

## Risks and Edge Cases
The randomized stress path can be nondeterministic and may miss rare collision patterns in short runs. Static counters and TDB state are process-global. The test treats inability to unlink by long name after short-name recreation as a failure but continues to clean up via the short path. Short-name support can be disabled or filesystem-dependent, making this suite sensitive to server/share configuration.

## Test Signals
Useful signals are collision counts, failures unlinking recreated files, successful alternate-name querying, successful short-name create/unlink, and successful SMB2 FIND with `SMB2_CONTINUE_FLAG_SINGLE` and a mangled mask.
