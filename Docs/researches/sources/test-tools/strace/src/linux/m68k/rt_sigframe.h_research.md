<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/m68k/rt_sigframe.h

## Purpose
Defines the `m68k` real-time signal-frame layout metadata used to locate saved signal masks.

## Important APIs, Types, and Functions
- Declares `struct_rt_sigframe` or `RT_SIGFRAME_UC_UCONTEXT_OFFSET`/`RT_SIGFRAME_UC_SIGMASK_OFFSET` constants for shared signal-frame code.

## Control Flow
- No runtime control flow; architecture signal-frame readers use these offsets when walking tracee stack memory.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `m68k`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/m68k/rt_sigframe.h`: 23 lines; 410 bytes; includes `# include <signal.h>`; defines `# define STRACE_RT_SIGFRAME_H`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/m68k/rt_sigframe.h -->
