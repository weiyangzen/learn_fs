# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/amd64-ucontext.h

## Purpose

This vendored header defines a minimal AMD64 `ucontext_t`/`mcontext_t` layout for platforms where `libcoroutine` uses private context save/restore routines rather than system `ucontext`. It targets Apple x86-64 through `taskimpl.h` and pairs with `asm.S` and `context.c`.

## Important APIs, types, and functions

It maps `setcontext()` and `getcontext()` to `setmcontext()` and `getmcontext()`, typedefs `mcontext_t` and `ucontext_t`, and declares `swapcontext()`, `makecontext()`, `getmcontext()`, and `setmcontext()`. `struct mcontext` stores AMD64 argument registers, callee-saved registers, trap metadata, `mc_rip`, `mc_rsp`, flags, FP format/ownership fields, XMM/FPU storage, and spare fields. `struct ucontext` holds signal mask, machine context, link, stack, and spare space.

## Control flow, state, and persistence

The file only defines layout and declarations. `context.c` fills `mc_rdi`, `mc_rsi`, `mc_rip`, and `mc_rsp` for new contexts; `asm.S` saves and restores the register slots. State is process-memory context snapshots inside coroutine objects.

## Dependencies and integration points

`taskimpl.h` includes this file for Apple x86-64 after renaming the system type names to `libthread_*`. `Coro.c` uses the resulting `ucontext_t` in its `USE_UCONTEXT` backend. `asm.S` uses fixed offsets corresponding to this struct, so this header and assembly must stay in lockstep.

## Risks and test signals

ABI and stack alignment are the key risks. If offsets diverge from `asm.S` or `makecontext()` stack setup, context switches can restore wrong registers. The header only captures the FP state shape expected by the vendored code. Test with Apple x86-64 `libcoro` builds, coroutine switch stress, and tests that pass pointer arguments through `makecontext()` startup.
