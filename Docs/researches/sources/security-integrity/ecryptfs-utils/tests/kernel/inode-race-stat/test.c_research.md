<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c_research.md`. Source lines read for this pass: 375.

## Purpose
Compiled kernel regression fixture for root-only inode size race regression for kernel bug 36002.

## Important APIs, Types, And Functions
`drop_cache`, `check_size`, child `do_test`, pipe protocol, and main loop. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates/truncates/syncs a file to changing sizes, drops caches, and fans out child stat checks over pipes. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
writes `/proc/sys/vm/drop_caches` and a single test file; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
stale plaintext inode size race signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inode-race-stat/test.c -->
