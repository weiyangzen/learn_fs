<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c_research.md`. Source lines read for this pass: 197.

## Purpose
Compiled kernel regression fixture for random sparse extension read/write verifier.

## Important APIs, Types, And Functions
`test_write`, `test_read`, `test_write_read`, and `test_exercise`. Uses standard POSIX file, process, signal, and sometimes inotify/klog APIs.

## Control Flow
writes small buffers at random offsets up to a limit, reads each back, verifies final size, and unlinks. Return codes distinguish pass, fail, and setup error where the fixture defines those constants.

## State And Persistence Behavior
one temporary file with sparse extents; no long-lived repository state is written by the fixture itself.

## Dependencies And Integration Points
Depends on the wrapper script for mounted eCryptfs context, compiler-produced executable, libc/POSIX syscalls, and privileges when the scenario drops caches or reads kernel logs.

## Risks And Edge Cases
Stress fixtures can be noisy, CPU-heavy, or privilege-sensitive. Timeout-based failures may indicate kernel hangs but can also reflect overloaded CI hosts.

## Test Signals
sparse write/read and size accounting signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/extend-file-random/test.c -->
