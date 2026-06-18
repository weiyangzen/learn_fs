# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/context.c

## Purpose

`context.c` implements missing `makecontext()` and `swapcontext()` functions for the vendored coroutine context layer. It complements the private `getmcontext`/`setmcontext` assembly and lets `Coro.c` use a ucontext-like API on Apple, old FreeBSD/OpenBSD i386, and Linux ARM.

## Important APIs, types, and functions

Depending on platform macros, the file defines `makecontext()` for PowerPC, i386, AMD64, and ARM, plus `swapcontext()` when `NEEDSWAPCONTEXT` is selected. The AMD64 implementation expects exactly two integer arguments, stores them into `mc_rdi` and `mc_rsi`, aligns the stack, writes a fake return address, and sets `mc_rip`/`mc_rsp`.

## Control flow, state, and persistence

Compile-time branches select the needed implementation. `makecontext()` mutates a provided `ucontext_t` by setting the initial stack pointer, program counter, and argument registers/stack slots. `swapcontext()` calls `getcontext()` on the outgoing context and, only on the initial return, calls `setcontext()` for the incoming context. There is no persistent state outside the mutated context objects.

## Dependencies and integration points

It includes `taskimpl.h`, which selects the correct vendored or system `ucontext_t` definition. `Coro.c` calls `makecontext()` from `Coro_setup()` and `swapcontext()` from `Coro_switchTo_()`. CMake includes this file in `coro` for non-Windows builds.

## Risks and test signals

The `makecontext()` variants depend on stack growth and alignment rules. AMD64 traps if called with an argument count other than two, matching the pointer-splitting convention in `Coro.c`; future callers must preserve that contract. ARM setup writes general registers but does not provide deep signal-mask behavior. Test by starting coroutines with pointer contexts, switching repeatedly, and validating on Apple x86/x86-64 and Linux ARM builds if those targets remain supported.
