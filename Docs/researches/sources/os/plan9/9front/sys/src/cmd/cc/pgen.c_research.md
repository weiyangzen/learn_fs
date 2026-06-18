# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pgen.c

Portable statement/code generation logic for the Plan 9 C compiler, sitting above machine-specific back-end emission.

Key behavior:
- `codgen` emits function entry pseudo-op, handles complex return values, first register argument movement, reachability diagnostics, final return branch, register optimization, and stack-safe argument area sizing.
- `supgen` generates code in suppressed mode for dead constant branches without preserving emitted instructions.
- `uncomma` evaluates left comma operands before returning the final expression node.
- `gen` handles statement-level AST operations: expression statements, noreturn calls, returns, labels, gotos, cases, switches, loops, `break`, `continue`, `if`, `USED`, and `SET`.
- Tracks `canreach`, `warnreach`, `breakpc`, `continpc`, `nbreak`, and `ncontin` for unreachable-code diagnostics and control-flow patching.
- `OSWITCH` collects cases and delegates table emission to `doswit`.
- `bcomplex` type-checks boolean tests, optionally recognizes constant conditions, and emits boolean branches through `boolgen`.
- `usedset` emits `ANOP` markers to represent variable use/set annotations.

Dependencies:
- Includes `gc.h`.
- Uses back-end hooks such as `gpseudo`, `gbranch`, `patch`, `cgen`, `regalloc`, `regfree`, `regret`, `gmove`, `regopt`, and switch lowering via `doswit`.

Research notes:
- This file owns statement control-flow lowering, not low-level instruction selection.
- Reachability warnings intentionally suppress some habitual or yacc-generated unreachable `break` cases.
