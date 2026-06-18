<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c_research.md`. Source lines read for this pass: 242.

## Purpose
Compiled kernel regression fixture for sparse lseek semantics verifier.

## Important APIs, Types, And Functions
single `main` with open/lseek/write/read/stat checks. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
first confirms lseek past EOF does not extend file, then writes markers around holes and verifies zero-filled holes and final size after reopen. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
creates and unlinks one file; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
sparse-file hole and size regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/llseek/test.c -->
