<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/thread.cpp -->
# sources/security-integrity/libcap/contrib/bug218607/thread.cpp

## Purpose
C++ threaded repro for bug218607. It checks that `psx_syscall6` mirrors `PR_SET_NO_NEW_PRIVS` across threads.

## Important APIs, Types, And Functions
Uses `std::thread`, `std::mutex`, `std::condition_variable`, raw `syscall(__NR_prctl, PR_GET_NO_NEW_PRIVS)`, and `psx_syscall6(__NR_prctl, PR_SET_NO_NEW_PRIVS, 1, ...)`.

## Control Flow
Worker thread records initial no-new-privs state, signals readiness, waits. Main records its initial state, calls psx to set no-new-privs, releases worker, then both record final state and print before/after values.

## State And Persistence Behavior
Mutates process/thread no-new-privs state, which is sticky for the process. Synchronization state is in globals protected by mutex/condition variable.

## Dependencies And Integration Points
Includes `<sys/psx_syscall.h>` and links against libpsx. Built by the local makefile.

## Risks And Edge Cases
No-new-privs cannot be unset, so repeated execution in the same process model is not possible. The pass condition assumes both threads transitioned from 0 to 1.

## Test Signals
Signals are printed before/after values and `PASSED` when both threads observe the psx-applied state.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/thread.cpp -->
