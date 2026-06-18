# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/init.c

Initialization table for `hoc` keywords, constants, and builtins.

- Installs language keywords: `proc`, `func`, `return`, `if`, `else`, `while`, `for`, `print`, and `read`.
- Installs numeric constants: `PI`, `E`, `GAMMA`, `DEG`, and `PHI`.
- Installs math builtins: trigonometric functions, inverse trig wrappers, hyperbolic wrappers, logs, exp, sqrt, integer conversion, and abs.
- Builtins are entered as `BLTIN` symbols with function pointers in `u.ptr`.

Dependencies are `hoc.h`, generated token definitions in `y.tab.h`, and math/libc functions.
