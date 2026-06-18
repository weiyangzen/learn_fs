# File Research: sources/os/bsd/dragonflybsd/sys/sys/stdarg.h

This header provides DragonFly's `stdarg` proxy definitions using machine/compiler varargs primitives.

Key responsibilities:
- Includes `<machine/stdarg.h>`.
- Defines `va_list` from `__va_list` if not already declared.
- Defines:
  - `va_start`
  - `va_arg`
  - `va_copy`
  - `va_end`
- Defines legacy `__va_copy` as `___va_copy`.

Important invariants:
- `va_copy` is exposed for kernel, C99 or newer, C++11 or newer, or non-strict ANSI compatibility.
- The implementation delegates all mechanics to machine/compiler builtins.

Research notes:
- This is a small compatibility wrapper around machine-level varargs support.
