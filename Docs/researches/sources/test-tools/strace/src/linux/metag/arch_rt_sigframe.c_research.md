<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c

## Purpose
Implements or selects the `metag` helper for locating an rt-signal frame on the tracee stack.

## Important APIs, Types, and Functions
- Provides `FUNC_GET_RT_SIGFRAME_ADDR` directly or includes another architecture's compatible implementation.

## Control Flow
- The helper reads the current stack pointer, applies the architecture frame offset, and returns zero if stack-pointer acquisition fails.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `metag`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c`: 15 lines; 293 bytes; includes `#include "rt_sigframe.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/metag/arch_rt_sigframe.c -->
