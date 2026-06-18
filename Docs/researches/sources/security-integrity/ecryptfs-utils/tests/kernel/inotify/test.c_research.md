<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c_research.md`. Source lines read for this pass: 651.

## Purpose
Compiled kernel regression fixture for inotify event propagation suite.

## Important APIs, Types, And Functions
`test_inotify`, helpers for access/modify/attrib/create/delete/move/close, and `inotify_test` table. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
sets a watch, performs one filesystem operation, waits with timeout, and verifies expected IN_* flags. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates/removes files and directories under a supplied path; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
inotify correctness signal across eCryptfs.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/inotify/test.c -->
