# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.c

## Purpose

`Coro.c` implements FoundationDB's old `libcoroutine` backend: stack allocation, coroutine startup, context setup, and cooperative switching. In this repository it is built into the `coro` static library when `COROUTINE_IMPL` is `libcoro`, and `fdbserver/coroimpl/CoroFlowCoro.actor.cpp` uses it to run coroutine-style worker code.

## Important APIs, types, and functions

Public functions are `Coro_new()`, `Coro_free()`, `Coro_stack()`, `Coro_stackSize()`, `Coro_setStackSize_()`, `Coro_bytesLeftOnStack()`, `Coro_stackSpaceAlmostGone()`, `Coro_initializeMainCoro()`, `Coro_startCoro_()`, `Coro_switchTo_()`, and private `Coro_setup()`. Internal startup helpers are `CallbackBlock`, `Coro_StartWithArg()`, and `Coro_Start()`. The file integrates with FoundationDB's `g_stackYieldLimit`, `setProfilingEnabled()`, and `criticalError()`.

## Control flow, state, and persistence

`Coro_new()` allocates a zeroed `Coro` and initializes requested stack size. `Coro_startCoro_()` creates a stack for the target coroutine, builds an initial machine context using `Coro_setup()`, then immediately switches to it. The startup trampoline calls the user callback with its context and aborts through `criticalError()` if the callback returns unexpectedly. `Coro_switchTo_()` updates `g_stackYieldLimit`, then switches through fibers, `swapcontext()`, or `setjmp`/`longjmp` depending on compile-time backend. `Coro_initializeMainCoro()` marks the current thread as the main coroutine and estimates its stack. State is held in `Coro` objects, allocated stacks, platform context objects, and the process-global stack-yield/profiling hooks.

## Dependencies and integration points

The file includes `Common.h`, `flow/Platform.h`, `Base.h`, `Coro.h`, and `taskimpl.h` for platform context declarations. CMake compiles it with `USE_UCONTEXT` on non-Windows and `USE_FIBERS` on Windows. `CoroFlowCoro.actor.cpp` wraps `Coro_startCoro_()` and `Coro_switchTo_()` in FoundationDB's coroutine thread-pool implementation. Valgrind integration optionally registers coroutine stacks.

## Risks and test signals

This file is highly ABI-sensitive. The `setjmp` fallback edits private `jmp_buf` fields on several architectures. The ucontext x86-64 path splits pointer arguments into two `unsigned int` values for `makecontext()`. Stack accounting assumes downward-growing stacks; the upward path is disabled. `Coro_allocStackIfNeeded()` sets `requestedStackSize` to zero when freeing an oversized stack, which can make a later allocation invalid if that branch is reached. Test signals are CoroFlow startup/shutdown tests, context switching under sanitizer/Valgrind, slow-task profiling behavior around switches, and stress tests that exercise stack-depth warnings through `g_stackYieldLimit`.
