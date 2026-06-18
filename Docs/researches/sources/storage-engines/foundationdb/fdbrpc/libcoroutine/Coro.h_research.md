# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.h

## Purpose

`Coro.h` declares the public coroutine object and selects the implementation backend. It is the API consumed by FoundationDB's old CoroFlow implementation.

## Important APIs, types, and functions

The header defines stack-size defaults (`CORO_DEFAULT_STACK_SIZE`, `CORO_STACK_SIZE_MIN`), backend macros (`USE_FIBERS`, `USE_UCONTEXT`, `USE_SETJMP`), `CORO_IMPLEMENTATION`, `CoroStartCallback`, and `struct Coro`. `struct Coro` stores requested/allocated stack sizes, stack pointer, optional Valgrind stack id, backend-specific context handle (`fiber`, `ucontext_t`, or `jmp_buf`), and `isMain`. It declares creation, destruction, stack, startup, switching, and setup APIs.

## Control flow, state, and persistence

The header has compile-time control flow that chooses fibers on Windows with fiber support, ucontext when `HAS_UCONTEXT` or a forced `USE_UCONTEXT` is present, and `setjmp` otherwise. Runtime state is the `Coro` object created by `Coro.c`; no state is persisted.

## Dependencies and integration points

On non-Windows it includes `taskimpl.h`; on ucontext builds it includes `<sys/ucontext.h>`. `fdbserver/coroimpl/CoroFlowCoro.actor.cpp` includes this header directly. CMake forces `USE_UCONTEXT` or `USE_FIBERS` for the `coro` target, so the auto-detection branch is usually overridden in FoundationDB builds.

## Risks and test signals

The main risks are backend selection drift and stack-size mismatch. Some platform branches depend on macros such as `HAS_UCONTEXT` that may not be consistently provided outside the configured CMake target. Test by building all supported `COROUTINE_IMPL=libcoro` platforms, checking `CORO_IMPLEMENTATION`, and running CoroFlow tests under normal and low-stack conditions.
