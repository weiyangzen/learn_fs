# File Research: sources/os/plan9/9front/sys/src/cmd/5c/gc.h

This header defines ARM backend data structures, globals, and function prototypes for `5c`.

Key contents:
- Includes common C compiler state from `../cc/cc.h` and ARM object definitions from `5.out.h`.
- Defines ARM C type widths, `FNX` complexity threshold, and `BTRUE` boolean-generation flag.
- Defines backend structures:
  - `Adr`: object operand address.
  - `Prog`: emitted instruction node.
  - `Case`/`C1`: switch case lists.
  - `Multab`/`Hintab`: multiply-by-constant optimization metadata.
  - `Var`: tracked variable for register allocation.
  - `Reg`: control-flow/data-flow graph node.
  - `Rgn`: candidate register-allocation region.
- Declares global backend state for control-flow targets, case lists, constants, emitted programs, registers, string data, safe temporaries, register allocation bitsets, CFG nodes, dominance helpers, and optimization flags.
- Defines liveness macros `BLOAD`, `BSTORE`, `LOAD`, `STORE`, and `bset`.
- Declares prototypes for code generation, text emission, switch/bitfield/string/output helpers, listing formatters, register allocation, peephole optimization, register-bit mapping, and predication helpers.
- Registers Plan 9 formatter pragmas for backend custom formats.

Dependencies and interactions:
- Included by all `5c` backend implementation files.
- Coordinates the common compiler front end with ARM-specific code generation and optimization.

Research relevance:
- This is the backend’s shared contract and data model.

Risk notes:
- `Prog.as`, registers, names, and condition bytes are narrow character fields, matching object format expectations.
- Global state is pervasive; backend functions depend on implicit current `p`, `pc`, `reg[]`, `cursafe`, and type tables.
