<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c_research.md`. Source lines read for this pass: 287.

## Purpose
Compiled kernel regression fixture for multi-process mkdir/rmdir stressor.

## Important APIs, Types, And Functions
`hang_check`, `test_dirs`, `test_exercise`, signal handlers, and duration CLI. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
forks workers per CPU; each syscall is wrapped in a child and `select` timeout to detect kernel hangs. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
no persistent state beyond temporary directories; relies on wrapper cleanup; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
mkdir/rmdir syscall latency and deadlock regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent/test.c -->
