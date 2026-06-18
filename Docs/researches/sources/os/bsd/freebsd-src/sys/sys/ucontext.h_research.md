# File Research: sources/os/bsd/freebsd-src/sys/sys/ucontext.h

User context and machine context public/kernel interface.

Key responsibilities:
- Includes signal, machine-dependent ucontext, and generic `_ucontext` definitions.
- Defines `UCF_SWAPPED`, used by `swapcontext(3)`.
- Declares userland `getcontext`, `getcontextx`, `setcontext`, `makecontext`, `signalcontext`, and `swapcontext`, plus BSD-visible internal helpers for extended context allocation/fill.
- Under `_KERNEL`, defines machine-independent `get_mcontext()` flag `GET_MC_CLEAR_RET` and declares machine-dependent `get_mcontext` and `set_mcontext` functions.

Dependencies:
- Depends on `sys/signal.h`, `machine/ucontext.h`, and `sys/_ucontext.h`.

Notable risks:
- User context APIs expose register/signal ABI details and are architecture-sensitive.
- `getcontext`/`__fillcontextx` are marked `__returns_twice`, which affects compiler assumptions.
