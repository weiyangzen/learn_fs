# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldo.c

## Role

`ldo.c` implements Lua's stack, call, protected-call, coroutine resume/yield, hook-call, and protected parser machinery.

## Main Responsibilities

- Implements error handling with a linked stack of `lua_longjmp` records.
- Uses a kernel-specific branch with `label_t`, `setjmp`, and `longjmp` under `_KERNEL`.
- Throws errors to thread or main-thread handlers, invokes panic functions when available, and panics if no error handler exists.
- Reallocates, grows, shrinks, and corrects stacks while preserving open upvalue and `CallInfo` pointers.
- Runs debug hooks safely with stack/top restoration and hook reentrancy suppression.
- Prepares C, C-closure, Lua-closure, and `__call` metamethod calls; handles varargs and missing fixed parameters.
- Completes calls by moving results to requested slots and restoring caller frames.
- Enforces C-call depth and non-yieldable call boundaries.
- Implements coroutine resume, recovery from yielded protected calls, continuation calls, `lua_yieldk`, and unrolling back to C boundaries.
- Implements protected calls and protected parser execution for text/binary chunks, with cleanup of scanner/parser dynamic buffers.

## Integration Points

This file is the control-flow center for `lapi.c`, `lvm.c`, parser/loading code, coroutines, hooks, and error reporting. It calls into `lfunc`, `lgc`, `lundump`, `lparser`, `lzio`, and `lvm`.

## Risk Notes

The highest-risk areas are non-local jumps, stack relocation, yielded continuations, protected-call recovery, and parser cleanup. Kernel embedding makes the `_KERNEL` longjmp path and panic behavior particularly important.
