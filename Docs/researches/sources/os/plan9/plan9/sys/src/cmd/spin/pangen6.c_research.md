# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.c

This file implements Spin’s AST/FSM slicing analysis for `spin -A`. It uses FSMs collected by `pangen5.c` to identify property-relevant statements, redundant variables/statements, channel aliases, control dependencies, and process-level simplification suggestions.

Key behavior:
- `AST_store()` records each non-claim/non-trace proctype FSM and start state for later slicing.
- `AST_track()` is called during parsing/property handling to collect initial slice criteria from assertions, claims, remote references, and relevant expressions.
- `AST_slice()` orchestrates the full pass: def/use computation, hidden assignment modeling, channel alias analysis, prelabeling assertions, iterative data/control dependency propagation, reporting, and suggestions.
- `def_use()`, `name_def_use()`, and `AST_def_use()` compute detailed use/def/deref-use/deref-def records for transitions, including structs and array indices.
- Channel alias analysis tracks aliases created by assignment, `run` parameters, and channel passing through send/receive.
- `AST_relevant()`, `def_relevant()`, and `AST_indirect()` mark transitions relevant when they define current slice variables, then add variables used by those definitions as new criteria.
- `AST_tagruns()` marks proctypes and `run` statements relevant when a target proctype or its parameters matter.
- `AST_ctrl()` and related helpers propagate control dependencies from blockable transitions that can reach relevant work.
- `AST_dominant()` computes dominators/reverse dominators to find subgraphs that can be treated as irrelevant for control-dependency purposes.
- Reporting functions identify redundant statements, redundant variables, predicate-abstraction candidates, source/sink processes, and buffer-like proctypes.

Important details:
- Relevance uses two bits: data relevance and control/blocking relevance, with `round` recording the iteration that marked a transition.
- Hidden assignments are made explicit for formal-actual parameter passing and initialized variables through synthetic `FSM_trans` records.
- Channel aliases are conservative; receive-based aliasing assumes possible matching sends with the same arity and argument position.
- Remote references mark referenced proctypes relevant.
- Claims, trace processes, and init processes are treated as inherently relevant in several passes.
- Dominator analysis uses bitsets over FSM states, then inverts edges to compute reverse dominance and identify proper subgraphs.
- The analysis intentionally ignores array indices for some mutual-variable comparisons and treats channel/struct cases conservatively.

Filesystem relevance:
- Indirect. This is static analysis over Promela models and generated FSMs, not filesystem code.
