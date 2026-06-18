# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Base.h

## Purpose

`Base.h` is a tiny common include guard for the vendored coroutine support. It centralizes standard C library includes needed by the old Steve Dekorte coroutine code and prevents repeated inclusion through `IOBASE_DEFINED`.

## Important APIs, types, and functions

There are no exported functions or data types. The file includes `stdio.h`, `stdlib.h`, `string.h`, `stddef.h`, `time.h`, `setjmp.h`, and `stdarg.h`.

## Control flow, state, and persistence

The file has no runtime behavior and no state. Its only effect is compile-time inclusion of common C declarations.

## Dependencies and integration points

`Coro.c` includes this file before using C runtime APIs and `jmp_buf`-related declarations. It is part of the `coro` static library when `COROUTINE_IMPL` is `libcoro`.

## Risks and test signals

Risk is low, but because this is a broad umbrella header, changes can affect old platform branches in `Coro.c`. Test by compiling the `coro` target across POSIX and Windows coroutine configurations.
