# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/run.c

This file implements the random/interactive simulator’s expression and statement execution engine. It evaluates Promela AST nodes and advances `Element` program counters.

Main execution functions:
- `eval_sub(Element *e)` evaluates one executable element or compound construct and returns the next `Element` to execute.
- `eval(Lextok *now)` evaluates expression/statement AST nodes and performs side effects for sends, receives, assignments, prints, `run`, assertions, and C fragments.
- `Enabled0(Element *e)` and `Enabled1(Lextok *n)` test whether a statement or compound branch is executable.
- `pc_enabled()` implements `enabled(pid)` by temporarily switching `X` to another running process.
- `complete_rendez()` is in `sched.c`, while this file’s `eval_sync()` restricts rendezvous partner matching to synchronous receives.

Important semantics:
- `eval_sub()` handles `GOTO`, `UNLESS`, `IF`, `DO`, `ATOMIC`, `D_STEP`, `NON_ATOMIC`, stop states, and normal statements.
- Branch choice is random unless interactive mode is active or `indstep` forces deterministic selection.
- Escape sequences are tested around normal statements unless replaying a trail; Java-like reverse escape priority is supported via `rev_escape()`.
- `D_STEP` and `ATOMIC` blocks splice their internal sequence into the outer continuation by setting the nested last element’s `nxt`.
- Rendezvous mode (`Rvous`) suppresses non-receive operations and changes behavior of gotos/else.
- `eval()` sets `lineno` and `Fname` before handling a node, keeping diagnostics tied to source location.

Side-effecting node support:
- `ASGN` goes through `assign()`, performs type checking, and delegates to `setval`.
- `ASSERT` reports failed assertions and may call `wrapup(1)`.
- `PRINT` and `PRINTM` go through `interprint()` and `printm()`, feeding `dotag()` for normal or MSC output.
- `C_CODE` and `C_EXPR` are uninterpreted in analysis mode and printed/evaluated through inline C plunking in simulation mode.

Risk notes:
- Arithmetic evaluation does not guard division/modulo by zero in this file.
- `interprint()` appends into fixed buffers and only checks length after formatting.
- Many functions temporarily mutate global flags such as `TstOnly`, `verbose`, `E_Check`, and `Escape_Check`.
