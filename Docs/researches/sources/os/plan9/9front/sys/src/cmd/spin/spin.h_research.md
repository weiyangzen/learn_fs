# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spin.h

`spin.h` is the shared structural and API contract for the Spin translator, simulator, and verifier generator. It defines the main AST, symbol, process, queue, flow, and FSM data structures used throughout `cmd/spin`.

Key definitions:
- Core enums: `btypes` for process/claim/trace categories, status-bit constants for `Element`, symbol hash size, channel x[rs] flags, code-fragment type IDs, and PROMELA type constants.
- `Lextok`: parse-tree node with token type, value, source location, symbol reference, sequence references, child links, inline id, and mtype marker.
- `Symbol`: unified symbol table entry with type, array/width metadata, initializers/runtime values, struct metadata, channel access metadata, scope/context/owner fields, and linked-list pointers.
- `Element`, `Sequence`, and `SeqList`: normalized control-flow representation built from parser output and consumed by interpreter/code generator.
- `RunList` and `ProcList`: runtime process instances and proctype definitions.
- `Queue`, `Label`, `Lbreak`, `Ordered`, `FSM_state`, `FSM_trans`, and `FSM_use`: queues, labels, break stacks, ordered symbol traversal, and pangen5 data-flow analysis.
- Declares a large cross-module function surface for parser helpers, symbol/type helpers, flow construction, code generation, queue operations, scheduler/runtime, diagnostics, LTL handling, and C-code support.

Important interactions:
- `YYSTYPE` is `Lextok *`, coupling this header directly to the yacc grammar.
- Many C files share mutable globals declared elsewhere rather than encapsulated module state.
- Scope support relies on `Symbol.context`, `Symbol.owner`, and `Symbol.bscp`.

Notable details:
- `TMP_FILE1` and `TMP_FILE2` are fixed temporary filenames used by LTL conversion/deferred parsing.
- Type constants double as bit-width values for integer-like PROMELA types.
