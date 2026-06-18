# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/asm.S

## Purpose

`asm.S` provides low-level `getmcontext`/`setmcontext` routines for platforms where `libcoroutine` needs a portable replacement for missing or unsuitable system context APIs. It covers legacy i386, AMD64, PowerPC, and ARM cases through preprocessor-selected assembly.

## Important APIs, types, and functions

The externally visible symbols are selected by macros `SET` and `GET`, usually `setmcontext`/`getmcontext` or underscored Apple variants. Conditional blocks define `NEEDX86CONTEXT`, `NEEDAMD64CONTEXT`, `NEEDPOWERCONTEXT`, and `NEEDARMCONTEXT`. Each `GET` stores enough registers into the matching `mcontext_t` layout, and each `SET` restores registers and transfers control to the saved PC/LR/RIP/EIP path.

## Control flow, state, and persistence

At compile time, OS/architecture macros select one assembly implementation. At runtime, `GET` snapshots current register state and returns 0; `SET` restores the stored context and resumes as though `GET` returned nonzero. This is the primitive used by `context.c`'s `swapcontext()` and by `Coro.c`'s ucontext backend. State is only the caller-provided `mcontext_t`.

## Dependencies and integration points

The assembly depends directly on the field offsets defined by `386-ucontext.h`, `amd64-ucontext.h`, `power-ucontext.h`, or Linux ARM system context layout. CMake includes this file in the `coro` target on Apple. It is also relevant for OpenBSD/i386 and Linux/ARM branches if built with the vendored context path.

## Risks and test signals

This is the highest-risk part of the coroutine support: register save sets, stack alignment, calling conventions, and symbol naming must match the platform exactly. PowerPC comments note missing vector/floating-point handling in the companion header, which can matter for code using those registers across coroutine switches. Test by running tight context-switch loops, CoroFlow workloads with optimized builds, and architecture-specific sanitizer/debugger checks for preserved callee-saved registers.
