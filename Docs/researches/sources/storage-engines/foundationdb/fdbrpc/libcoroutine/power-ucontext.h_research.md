# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/power-ucontext.h

## Purpose

This header defines a minimal PowerPC context layout for vendored coroutine context switching. It is used by `taskimpl.h` on non-x86 Apple and some OpenBSD fallback paths.

## Important APIs, types, and functions

The file maps `setcontext()`/`getcontext()` to `_setmcontext()`/`_getmcontext()`, typedefs `mcontext_t` and `ucontext_t`, and declares `makecontext()`, `swapcontext()`, `_getmcontext()`, and `_setmcontext()`. `struct mcontext` stores link register/program counter, condition register, counter, XER, stack pointer, TOC, first argument/return register `r3`, and callee-saved `r13` through `r31`. `struct ucontext` includes a simple stack object, signal mask, and machine context.

## Control flow, state, and persistence

No runtime control flow exists in the header. `asm.S` fills/restores the context fields, and `context.c` uses them to prepare new stacks and function entry. State is per-context process memory.

## Dependencies and integration points

It requires `ulong`, `uint`, and `sigset_t` declarations from `taskimpl.h` and system includes. It integrates with the `NEEDPOWERCONTEXT` and `NEEDPOWERMAKECONTEXT` code paths in `asm.S` and `context.c`.

## Risks and test signals

The header explicitly does not save vector or floating-point state, so code relying on those callee-saved registers across coroutine switches can break. Type assumptions for `ulong`/`uint` also make it sensitive to include order. Test signals are successful old PowerPC builds, preserved scalar callee-saved registers across switches, and workload tests that would expose FP/vector corruption if this target is used.
