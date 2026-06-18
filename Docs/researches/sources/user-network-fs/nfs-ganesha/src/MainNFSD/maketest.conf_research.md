<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf

## Purpose
Legacy maketest-style configuration for a static log/hash library test. It declares the product, command, success criteria, and classified failure patterns.

## Important APIs, Types, And Functions
- `Test Test_libloghash_Static` names the test.
- `Command = ksh ../scripts/run_test_liblog.ksh` runs the script.
- `Success TestOk` checks stdout and exit status.
- Failure clauses classify bad value, bad init, bad delete, bad statistics, missing key, and redundant key cases.

## Control Flow
The harness runs the shell command and evaluates status/stdout regexes to mark success or a named failure.

## State And Persistence Behavior
No daemon state. Any artifacts come from the invoked script.

## Dependencies And Integration Points
Depends on the maketest harness, `ksh`, and `../scripts/run_test_liblog.ksh`. It is colocated with MainNFSD but tests log/hash behavior.

## Risks
- Likely legacy; output regexes and command path may be stale.
- French output matching is brittle.
- Does not cover the MainNFSD files in this subset.

## Test Signals
Run the harness, verify `ksh`, confirm expected output phrases, and decide whether the test belongs in active CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/maketest.conf -->
