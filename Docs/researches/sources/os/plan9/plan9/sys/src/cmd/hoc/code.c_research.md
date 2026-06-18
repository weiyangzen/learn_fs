# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/code.c

Runtime virtual machine and execution engine for `hoc`.

- Defines fixed-size operand stack (`NSTACK 256`), instruction array (`NPROG 2000`), program counter, subprogram base, and call frame stack (`NFRAME 100`).
- Implements stack primitives, code emission, and instruction dispatch through `execute()`.
- Implements control-flow bytecodes for `while`, `for`, and `if`.
- Implements function/procedure definitions, calls, formal binding, saved variable restoration, and returns.
- Implements arithmetic, comparisons, boolean operations, exponentiation, assignment, compound assignment, increment/decrement, variable evaluation, builtins, printing, string printing, and `read()`.
- Uses `execerror()` for runtime errors and recovery.

Dependencies are `hoc.h`, generated `y.tab.h`, Plan 9 `bio`, `libc`, and math wrappers in `math.c`.

Notable concerns: fixed VM limits cause runtime errors for deep stacks, oversized programs, and deeply nested calls. `modeq()` casts through `long`, unlike `mod()` which uses `fmod`.
