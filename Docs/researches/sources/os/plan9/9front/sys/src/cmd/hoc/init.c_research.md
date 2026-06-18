# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/init.c

Installs `hoc` keywords, constants, and builtin functions into the symbol table.

Key points:
- Registers keywords: `proc`, `func`, `return`, `if`, `else`, `while`, `for`, `print`, and `read`.
- Registers constants: `PI`, `E`, `GAMMA`, `DEG`, and `PHI`.
- Registers builtins: trigonometric functions, checked inverse/hyperbolic/log/exp/sqrt wrappers, integer conversion, and absolute value.
- Builtin symbols are initially installed as `BLTIN`, then their function pointer is written to `s->u.ptr`.

Dependencies and interactions:
- Uses token values from `y.tab.h`.
- Calls `install` from `symbol.c`.
- Checked builtin wrappers are implemented in `math.c`.

Research relevance:
- This file defines the initial language environment available to every `hoc` session.
