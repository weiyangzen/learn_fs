<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c_research.md`. Source lines read for this pass: 100.

## Purpose
Compiled kernel regression fixture for symlink readlink/lstat length checker.

## Important APIs, Types, And Functions
single `main` creating a symlink to argv path. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
creates a file and symlink, calls readlink and lstat, and passes if returned target length equals `st_size`. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates and removes a file plus symlink; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
symlink metadata size regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/lp-524919/test.c -->
