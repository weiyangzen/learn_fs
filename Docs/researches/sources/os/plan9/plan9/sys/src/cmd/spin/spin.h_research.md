# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spin.h

This is the central shared header for the Spin front end, simulator, and pan-code generator sources in this directory.

Core type definitions:
- `Lextok`: AST node with token type, value, source location, inline id, symbol, sequence/list links, and left/right children.
- `Symbol`: symbol-table entry with name, unique id, type, visibility/hidden flags, array and bit-width metadata, runtime values, struct metadata, channel access metadata, initializer, owner/context, and next link.
- `Queue`: runtime channel instance with queue id, length, slot/field counts, field widths, contents, and send-step metadata.
- `Element`: executable control-flow node with AST pointer, global/local sequence numbers, merge metadata, status bits, sub/escape sequences, and linked-list edges.
- `Sequence` and `SeqList`: statement sequence and lists of alternatives.
- `Label`: label binding to symbol, context, element, inline id, visibility, and next link.
- `RunList` and `ProcList`: active runtime process instance and parsed proctype/claim/init/trace definition.
- FSM/dataflow types used by pangen slicing logic: `FSM_state`, `FSM_trans`, and `FSM_use`.

Important enums and constants:
- Process/body categories: `NONE`, `N_CLAIM`, `I_PROC`, `A_PROC`, `P_PROC`, `E_TRACE`, `N_TRACE`.
- Element status flags: `DONE`, `ATOM`, `L_ATOM`, `I_GLOB`, `DONE2`, `D_ATOM`, `ENDSTATE`, `CHECK2`, `CHECK3`.
- Symbol/channel/type constants: `XR`, `XS`, `XX`, `CODE_FRAG`, `CODE_DECL`, `PREDEF`, `UNSIGNED`, `BIT`, `BYTE`, `SHORT`, `INT`, `CHAN`, `STRUCT`.
- Size constants: `Nhash`, `SOMETHINGBIG`, `RATHERSMALL`, `MAXSCOPESZ`.

The header also defines `YYSTYPE` as `Lextok *`, null sentinels `ZN`, `ZS`, `ZE`, portability write mode `MFLAGS`, and a broad set of prototypes spanning parsing, scheduling, evaluation, channel operations, code generation, struct handling, C-code embedding, labels, assertions, trail replay, and diagnostics.

Architectural role:
- This header exposes most subsystem boundaries through C prototypes rather than opaque interfaces.
- It makes `Lextok`, `Symbol`, and `Element` the shared currency across parser, scheduler, simulator, product builder, and verifier generator.

Risk notes:
- The shared structures are large and mutable, with many fields reused by different phases.
- Several fields encode phase-specific meaning, so invariants are distributed across many `.c` files.
