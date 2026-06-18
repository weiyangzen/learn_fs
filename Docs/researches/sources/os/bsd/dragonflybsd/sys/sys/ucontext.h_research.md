# File Research: sources/os/bsd/dragonflybsd/sys/sys/ucontext.h

## Summary
Userland ucontext API declaration wrapper.

## Main Responsibilities
- Includes machine-independent `_ucontext` definitions.
- Declares `getcontext`, `setcontext`, `makecontext`, and `swapcontext` under BSD or older POSIX visibility.
- Declares DragonFly BSD quick context helpers under BSD visibility.

## Important Behavior
The POSIX context functions are hidden for POSIX.1-2008 and newer unless BSD visibility is enabled, matching their obsolescent status.

## Risks
Context switching APIs are ABI- and architecture-sensitive. The quick variants are nonstandard DragonFly extensions and should not be assumed portable.
