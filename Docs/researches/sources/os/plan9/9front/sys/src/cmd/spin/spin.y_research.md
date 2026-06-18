# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spin.y

`spin.y` is the yacc grammar for PROMELA plus embedded LTL syntax. It builds `Lextok` AST nodes, creates proctype/claim/trace definitions, registers declarations and typedefs, expands inline/C fragments, and records semantic feature flags used by the simulator and verifier generator.

Key responsibilities:
- Defines tokens and precedence for PROMELA statements, expressions, channels, priorities, inline code, claims, traces, and LTL operators.
- Parses top-level units: proctypes, `init`, never claims, inline LTL formulas, trace/event assertions, declarations, typedefs, C fragments, and inline definitions.
- Builds proctype bodies and starts active processes via `ready`, `runnable`, and `announce`.
- Parses declarations for primitive types, mtypes, arrays, channels, and user-defined structs, calling `setptype`, `setutype`, `setmtype`, and structure expansion helpers.
- Parses statements: assignments, sends/receives, random receives, sorted sends, assertions, prints, inline calls, returns, `if/do`, `for`, `select`, `atomic`, `d_step`, non-atomic blocks, labels, gotos, breaks, `unless`, and channel probes.
- Parses expressions: arithmetic, bitwise, comparisons, boolean operators, ternary-like arrow form, `run`, `len`, `enabled`, priority access, queue poll, constants, timeout, `np_`, `pc_value`, remote label/variable references, and LTL expressions.
- Converts embedded LTL ASTs to string formulas in `ltl_to_string`, using `recursive` to print formula syntax, then passes them to the existing LTL translation pipeline.
- Provides `yyerror` wrapper and disabled `sanity_check`.

Important interactions:
- `context`, `owner`, `Expand_Ok`, `initialization_ok`, `has_*` feature flags, and `NamesNotAdded` are modified throughout grammar actions.
- Struct references are expanded with `mk_explicit` when formals or message parameters require flattening.
- Channel-use tracking is attached during send/receive/run parsing.
- Inline call argument text collection is coordinated with `spinlex.c` through `IArgs`.

Notable details:
- `ltl_to_string` writes to `TMP_FILE1`, reads back the formula, unlinks the file, and stores the formula as a symbol name.
- A duplicate `expr IMPLIES expr` production is present in the file. It appears to be a duplicated grammar line in the imported source.
