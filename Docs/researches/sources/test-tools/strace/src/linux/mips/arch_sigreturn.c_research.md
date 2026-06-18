<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/mips/arch_sigreturn.c

## Purpose
Decodes legacy `mips` sigreturn frames to print the signal mask restored by the kernel.

## Important APIs, Types, and Functions
- `arch_sigreturn(struct tcb *tcp)` reads the stack pointer and signal-context data with `umove_or_printaddr`/`umoven_or_printaddr`, then calls `tprintsigmask_addr`.

## Control Flow
- Fetch stack pointer, locate the architecture sigcontext, read the saved signal-mask words, and print them if all required reads succeed.

## State and Persistence Behavior
- No persistent state; the code reads tracee stack memory for the current signal-return syscall decode.

## Dependencies and Integration Points
- Integrated by strace signal-return decoders and common signal-frame helpers.
- Depends on kernel signal-frame ABI, `struct sigcontext`, `siginfo_t`, and shared stack-pointer helpers.

## Risks and Edge Cases
- Signal-frame offsets are kernel ABI contracts and differ sharply between normal, compat, and rt signal returns.
- Bad offsets can make strace print bogus masks or dereference invalid tracee addresses.

## Test Signals
- Trace signal delivery and `sigreturn`/`rt_sigreturn` on `mips`.
- Validate printed masks against a test program that blocks a known signal set before handler return.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_sigreturn.c`: 24 lines; 513 bytes; functions `arch_sigreturn`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_sigreturn.c -->
