# sources/test-tools/strace/src/linux/x32/arch_rt_sigframe.c

## Purpose
Reuses x86_64 real-time signal-frame address calculation for x32, which itself includes the i386 implementation.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_rt_sigframe.c`; that file includes `../i386/arch_rt_sigframe.c`, providing `get_rt_sigframe_addr` logic.

## Control Flow and Integration
Used by generic `rt_sigreturn.c` to locate the signal frame on the tracee stack before reading `struct_rt_sigframe` fields. The actual control flow is inherited from i386-compatible code.

## State and Persistence
No persistent state; reads current tracee stack/register state.

## Dependencies
Depends on x86/i386 signal-frame conventions and generic rt-sigreturn decoder.

## Risks
x32 signal-frame layout is a compatibility edge case. Reusing i386 logic through x86_64 must match kernel behavior for x32 rt signal frames.

## Test Signals
x32 signal-return tests should verify `rt_sigreturn` prints restored signal masks and handles bad frame addresses cleanly.
