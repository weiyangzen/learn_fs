# sources/test-tools/strace/src/linux/tile/rt_sigframe.h

## Purpose
Defines the Tile real-time signal frame shape used by generic `rt_sigreturn` decoding.

## Important APIs, Types, and Functions
Declares `struct_rt_sigframe` with `save_area[C_ABI_SAVE_AREA_SIZE]`, `siginfo_t info`, and `ucontext_t uc`. It includes `<signal.h>` and uses an include guard.

## Control Flow and Integration
No functions are present. `rt_sigreturn.c` includes this type through `DEF_MPERS_TYPE(struct_rt_sigframe)` and computes offsets such as `uc.uc_sigmask` for decoding saved signal masks.

## State and Persistence
No state. The type definition is compile-time metadata describing tracee memory layout.

## Dependencies
Depends on `C_ABI_SAVE_AREA_SIZE`, libc/kernel definitions of `siginfo_t` and `ucontext_t`, and the generic rt-sigframe decoding path.

## Risks
Any mismatch with the kernel's Tile sigframe layout makes strace read the wrong fields during signal-return decoding. Header definitions from the build environment must match the target ABI.

## Test Signals
Tile `rt_sigreturn` tests should validate signal-mask decoding. Static layout checks around `offsetof(struct_rt_sigframe, uc.uc_sigmask)` are useful if available.
