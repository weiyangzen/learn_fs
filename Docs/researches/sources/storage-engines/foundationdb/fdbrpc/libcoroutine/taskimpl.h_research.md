# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/taskimpl.h

## Purpose

`taskimpl.h` is the platform selection layer inherited from Russ Cox-style coroutine/task code. It configures `ucontext` availability, pulls in system headers, and substitutes vendored context definitions for platforms with broken or removed `ucontext` APIs.

## Important APIs, types, and functions

The file defines utility macros `nil` and `nelem()`, SunOS makecontext feature macros, `USE_UCONTEXT` overrides for OpenBSD and macOS 10.5+, Apple/OpenBSD type renames to `libthread_mcontext_t`/`libthread_ucontext_t`, and declarations for legacy FreeBSD and ARM `getmcontext()`/`setmcontext()` APIs. Large commented-out `Task` definitions document the original library lineage but are not active.

## Control flow, state, and persistence

All behavior is compile-time. The header decides whether `<ucontext.h>` is included and whether local `386-ucontext.h`, `amd64-ucontext.h`, or `power-ucontext.h` is used. It holds no runtime state.

## Dependencies and integration points

`Coro.h`, `Coro.c`, and `context.c` include this file on non-Windows builds. It depends on POSIX headers such as `unistd.h`, `sys/time.h`, `signal.h`, `sys/utsname.h`, and `inttypes.h`. The CMake `coro` target forces `USE_UCONTEXT` on non-Windows, but this header can still undefine or replace parts for specific OSes.

## Risks and test signals

Because it uses broad platform macros and type renaming, subtle OS version changes can select the wrong context path. OpenBSD forcibly disables `USE_UCONTEXT`, while CMake may define it, so build behavior should be verified if that target matters. Test by compiling `coro` across configured platforms, ensuring no system/vendored `ucontext_t` conflicts, and running context switch smoke tests.
