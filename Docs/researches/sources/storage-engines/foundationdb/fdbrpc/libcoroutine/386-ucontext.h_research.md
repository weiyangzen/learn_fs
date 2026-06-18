# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/386-ucontext.h

## Purpose

This vendored header defines a minimal i386 `ucontext_t`/`mcontext_t` ABI for platforms where FoundationDB's old `libcoroutine` cannot rely on a usable system `ucontext` implementation. It maps `getcontext` and `setcontext` to private `getmcontext`/`setmcontext` routines implemented in `asm.S`, allowing `Coro.c` and `context.c` to build portable user-space context switching on older BSD/OpenBSD/Apple-style environments.

## Important APIs, types, and functions

The file exposes `mcontext_t`, `ucontext_t`, `swapcontext()`, `makecontext()`, `getmcontext()`, and `setmcontext()`. `struct mcontext` stores i386 segment registers, general registers, trap/error fields, instruction pointer, stack pointer, flags, and x87 floating-point storage. `struct ucontext` carries a signal mask, machine context, link, stack, and spare space. The first context fields intentionally match older `sigcontext` layout assumptions.

## Control flow, state, and persistence

The header itself has no runtime control flow. Its layout controls how assembly saves/restores register state and how `context.c` writes new instruction and stack pointers in `makecontext()`. Runtime state is entirely in caller-owned `ucontext_t` instances, usually inside `struct Coro`. Nothing is persisted beyond process memory.

## Dependencies and integration points

It assumes `sigset_t` and `stack_t` are visible before inclusion through `taskimpl.h`/system headers. `taskimpl.h` includes it for Apple i386 and OpenBSD i386 after renaming the public type names to `libthread_*` names, avoiding direct collision with system headers. `asm.S` depends on the exact byte offsets of the i386 `mcontext` fields, and `context.c` depends on `mc_eip` and `mc_esp`.

## Risks and test signals

The risk is ABI drift: any field reorder, size mismatch, or platform where `sigset_t`/`stack_t` differs from the assumed layout can corrupt registers or crash on context switch. The file also does not model modern SIMD state beyond the old x87 block. Test signals are successful build on the targeted legacy i386 platforms, coroutine creation/switch tests, and FoundationDB CoroFlow workloads completing without stack/register corruption.
