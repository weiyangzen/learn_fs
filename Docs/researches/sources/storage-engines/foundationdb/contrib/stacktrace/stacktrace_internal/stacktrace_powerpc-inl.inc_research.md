# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_powerpc-inl.inc

## Purpose
This file implements PowerPC stack unwinding for ABI variants that preserve a stack chain. It handles PowerPC-specific link-register storage and has Linux signal-frame support.

## Important APIs, Types, And Functions
`StacktracePowerPCGetLR` returns the saved link register from ABI-specific stack slots. `NextStackFrame<STRICT_UNWINDING, IS_WITH_CONTEXT>` validates stack-chain transitions, enforces 16-byte alignment, and can recover pre-signal state from `ucontext_t`. `StacktracePowerPCDummyFunction` forces the link register to be saved. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` performs the actual stack walk and frame-size reporting.

## Control Flow
`UnwindImpl` reads register `r1` into `sp` via inline assembly, calls the dummy function, skips the top link-register save area, then advances once before entering the main loop because PowerPC stores return addresses in the caller's frame. Linux signal support resolves `__kernel_sigtramp_rt64` through VDSO, detects signal trampoline frames, and can replace the next stack pointer with `PT_R1` from the signal context after readability checks.

## State And Persistence
The Linux signal path keeps static cached kernel-symbol status and trampoline address. No durable persistence exists.

## Dependencies And Integration Points
Dependencies include PowerPC ABI macros, inline assembly, Linux `asm/ptrace.h`/`ucontext.h`, VDSO support, `AddressIsReadable`, and sanitizer-suppression attributes. It is selected for `__ppc__` or `__PPC__` when frame pointers are available.

## Risks
ABI detection is brittle; unsupported ABI macros produce a compile-time error. Link-register placement differs across Darwin/AIX/SYSV/PPC64, and a wrong selection corrupts PCs. Signal support is Linux-specific and assumes VDSO symbol availability. The unwinder reads raw stack memory and suppresses sanitizer instrumentation for that reason.

## Test Signals
Testing should include PPC32/PPC64 ABI variants, Linux signal-handler traces, alternate stacks, frame-size reporting, and capped dropped-frame counting. Cross-compilation alone is not enough because runtime ABI stack layout matters.
