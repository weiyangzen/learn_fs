# sources/user-network-fs/samba/source4/torture/local/smbtorture_fullname.c

## Purpose
This tiny file creates a deliberately nested local smbtorture suite to exercise full test-name handling.

## Important APIs, types, and functions
`test_smbtorture_always_pass()` always returns true. `torture_local_smbtorture()` creates suites `smbtorture`, `level1`, `level2`, and `level3`, nests them, and adds `always_pass` at the deepest level.

## Control flow
Suite construction creates a three-level hierarchy, attaches child suites from deepest to top-level, and returns the root suite to `local.c`.

## State and persistence behavior
Only in-memory suite metadata is created. No external state is read or written.

## Dependencies and integration points
The file integrates with the local suite registry and smbtorture's naming/reporting logic.

## Risks and edge cases
The useful behavior is in the harness: regressions would show as incorrect fully qualified names or failure to run nested tests.

## Test signals
The always-pass test confirms deeply nested suite registration and reporting can execute a leaf test successfully.
