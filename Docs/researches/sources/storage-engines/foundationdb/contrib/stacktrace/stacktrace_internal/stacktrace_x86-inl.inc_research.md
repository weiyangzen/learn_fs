# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_x86-inl.inc

## Purpose
This file implements x86 and x86_64 frame-pointer unwinding for the stacktrace library. It contains extra Linux/i386 logic to unwind across VDSO system-call and signal trampoline frames.

## Important APIs, Types, And Functions
`CountPushInstructions` analyzes the i386 VDSO `__kernel_vsyscall` instruction prefix to understand how the kernel wrapper saved registers. `GetFP` extracts plausible base or stack pointers from Linux `ucontext_t`. `NextStackFrame<STRICT_UNWINDING, WITH_CONTEXT>` validates and advances the frame pointer with signal-context exceptions. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` records return addresses from `fp + 1`, optional frame sizes, and dropped-frame estimates.

## Control Flow
`UnwindImpl` starts from `__builtin_frame_address(0)` and loops until max depth, null/self frames, or failed validation. Strict mode enforces monotonic upward frame addresses and a 100KB max frame; non-strict mode allows discontiguous frames but checks readability. In Linux i386 signal mode, it resolves `__kernel_rt_sigreturn` and `__kernel_vsyscall` from VDSO, detects when `%ebp` cannot be used, and restores the next frame pointer from saved `%esp`.

## State And Persistence
Linux i386 VDSO analysis stores static `num_push_instructions` and VDSO symbol addresses. No durable state exists.

## Dependencies And Integration Points
The implementation depends on GCC builtins, x86 frame-pointer ABI, Linux `ucontext_t`, VDSO support, `AddressIsReadable`, and sanitizer-suppression attributes. It is the primary selected unwinder for `__i386__` and `__x86_64__` with frame pointers.

## Risks
The file assumes frame pointers and rejects implausible chains; optimized leaf functions or code compiled with omitted frame pointers can truncate or corrupt traces. i386 VDSO instruction parsing is deliberately narrow and asserts on unexpected instruction sequences. Non-strict readability checks are slower and still cannot guarantee semantic validity of PCs.

## Test Signals
Useful coverage includes x86_64 and i386 builds, signal-handler unwinding, omitted-frame-pointer negative tests, VDSO-enabled kernels, `max_depth == 0`, frame-size output, and dropped-frame counts under shallow depth.
