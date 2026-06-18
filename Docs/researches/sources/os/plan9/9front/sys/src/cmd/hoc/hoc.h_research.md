# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.h

Declares the shared data structures and function prototypes for the `hoc` interpreter.

Key points:
- Defines `Inst` as a function-pointer instruction type and `STOP` as the null instruction.
- Defines:
  - `Symbol` for names, token/type, value/definition/string payload, and symbol-list link.
  - `Symval` union for numeric values, builtin function pointers, function definitions, and strings.
  - `Datum` stack union for numbers or symbol references.
  - `Saveval` for saved formal-variable values during calls.
  - `Formal` for formal parameter lists.
  - `Fndefn` for function/procedure code pointers, formals, and arity.
- Declares symbol, VM, arithmetic, control-flow, call/return, parser, initialization, allocation, and math helper functions.
- Exposes global code-generation pointers `progp`, `progbase`, and `prog`.

Dependencies and interactions:
- Shared by `code.c`, `hoc.y`, `init.c`, `math.c`, and `symbol.c`.
- Token constants are supplied separately by `y.tab.h`.

Research relevance:
- This file is the ABI between the lexer/parser, symbol table, math wrappers, and VM runtime.
