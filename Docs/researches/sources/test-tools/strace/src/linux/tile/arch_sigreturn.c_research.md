# sources/test-tools/strace/src/linux/tile/arch_sigreturn.c

## Purpose
Prints the signal mask restored by Tile's old `sigreturn` path. It computes the mask address inside the kernel signal frame from the tracee stack pointer and delegates decoding to `print_sigset_addr`.

## Important APIs, Types, and Functions
Defines static `arch_sigreturn(struct tcb *tcp)`. It calls `get_stack_pointer`, uses `C_ABI_SAVE_AREA_SIZE`, `sizeof(siginfo_t)`, and `offsetof(ucontext_t, uc_sigmask)`, then calls `print_sigset_addr(tcp, addr)`.

## Control Flow and Integration
Called from generic `sigreturn.c` during decoding. If stack pointer retrieval fails, it returns without output. Otherwise it adds the Tile sigframe ucontext offset and prints the saved signal mask.

## State and Persistence
No state is modified except normal output state. It reads tracee memory indirectly through `print_sigset_addr`.

## Dependencies
Depends on Tile ABI frame layout matching `rt_sigframe.h`, libc/kernel `ucontext_t`, `siginfo_t`, and generic stack-pointer helpers.

## Risks
The offset is layout-sensitive. Changes in Tile sigframe ABI, incorrect `C_ABI_SAVE_AREA_SIZE`, or mismatched headers can make strace read the wrong signal-mask address. Failure to fetch the stack pointer produces intentionally silent incomplete decoding.

## Test Signals
Tile signal-return tests should verify printed signal masks for `sigreturn` and `rt_sigreturn`. ABI offset checks against kernel headers or crafted signal frames are useful regression signals.
