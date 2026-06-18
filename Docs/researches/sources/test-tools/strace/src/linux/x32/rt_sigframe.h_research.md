# sources/test-tools/strace/src/linux/x32/rt_sigframe.h

## Purpose
Reuses the x86_64 real-time signal-frame description for x32 by including `../x86_64/rt_sigframe.h`.

## Important APIs, Types, And Data
The included x86_64 header defines `struct_rt_sigframe` for non-`__i386__` builds as a typedef containing `kernel_ulong_t pretcode`, `ucontext_t uc`, and a comment that more data follows. If compiled under `__i386__`, the included header redirects to the i386 signal-frame definition instead.

## Control Flow
There is no runtime control flow. Preprocessor conditions in the included header select either the i386 frame or the x86_64-style frame. In the x32 architecture directory, the intended effective path is the x86_64-style structure with x32-compatible `kernel_ulong_t` sizing from the surrounding build configuration.

## State And Persistence
No mutable state. The typedef describes stack memory laid out by the kernel when delivering real-time signals. Strace uses this layout knowledge to inspect or decode signal-return state; the actual persistent state is the tracee's signal frame on its stack.

## Dependencies And Integration Points
Depends on `signal.h`, `ucontext_t`, `kernel_ulong_t`, and the x86_64 signal-frame header. Integrates with architecture signal-return decoding and any code that needs to locate saved context from an rt signal frame.

## Risks
Signal frame layouts are ABI-sensitive. Reusing x86_64 structure shape is appropriate for x32 only if `kernel_ulong_t` and libc `ucontext_t` definitions match the kernel ABI expectations. Mismatches can cause incorrect stack reads or misdecoded signal-return arguments. The trailing "more data follows" means consumers must not assume the typedef covers the full frame.

## Test Signals
Signal-return decoding tests on x32 should verify that saved context fields are read correctly. Build coverage for both x32 and non-x32 x86_64 paths should confirm the include path and guard behavior. Runtime tests that trace a signal handler returning through `rt_sigreturn` are the highest-value signal.

## Source-Read Signal
Reviewed the complete local file and the complete included x86_64 signal-frame header.
