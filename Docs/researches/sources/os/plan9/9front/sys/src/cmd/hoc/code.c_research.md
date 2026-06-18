# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/code.c

Implements the virtual machine/runtime for the `hoc` calculator language.

Key points:
- Maintains a fixed-size value stack, instruction array, program counter, current code-generation pointer, and function/procedure call frame stack.
- Provides stack primitives `push`, `pop`, and `xpop`.
- Emits bytecode-like instructions with `code()` and runs them with `execute()`.
- Implements control-flow instructions for `while`, `for`, and `if` by executing saved instruction spans and updating `pc`.
- Implements function/procedure definition and call support:
  - `define` stores code start, formals, and arity.
  - `call` checks arity, saves formal variable values, binds arguments, and executes function code.
  - `restore`, `restoreall`, `funcret`, and `procret` restore dynamic bindings and manage return values.
- Implements arithmetic, comparison, logical, power, unary, assignment, compound assignment, pre/post increment/decrement, builtin-function call, variable evaluation, print, string print, and read-into-variable operations.
- Uses `execerror` for stack overflow/underflow, undefined variables, non-variable assignments, division by zero, and bad returns.

Dependencies and interactions:
- Includes `hoc.h` and yacc token definitions from `y.tab.h`.
- Uses symbol table functions from `symbol.c`, math wrappers from `math.c`, and parser-generated code from `hoc.y`.
- Uses Plan 9 `Biobuf` input for `read()` expressions.

Research relevance:
- This is the core interpreter runtime for `hoc`, separating grammar/code generation from executable semantics.
