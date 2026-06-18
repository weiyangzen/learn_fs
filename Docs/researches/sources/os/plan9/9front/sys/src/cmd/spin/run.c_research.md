# File Research: sources/os/plan9/9front/sys/src/cmd/spin/run.c

`run.c` implements Spin's random-simulation execution engine for PROMELA parse tree nodes and control-flow elements. It depends on `spin.h` data structures, parser token IDs from `y.tab.h`, scheduler globals from `sched.c`, queue/message helpers, label/control-flow helpers, and printing/commenting helpers.

Key responsibilities:
- Provides deterministic pseudo-random generation through `Srand` and `Rand`, used for nondeterministic scheduling and option selection.
- Executes one `Element` or compound subtree with `eval_sub`, handling `goto`, `unless`, `if`, `do`, `atomic`, `d_step`, non-atomic blocks, escape sequences, rendezvous restrictions, interactive choice prompting, and trail replay constraints.
- Evaluates expression and statement `Lextok` nodes with `eval`, covering arithmetic, boolean operators, queue probes, sends/receives, `run`, `enabled`, priority operations, `pc_value`, `np_`, assertions, prints, C fragments, assignments, and remote references.
- Implements assignment typing through `assign`, using `Sym_typ`, `typ_ck`, `setval`, and structure tracking checks.
- Implements executable-state checks through `Enabled1` and `Enabled0`, conservatively treating side-effecting statements as enabled while probing channel operations without committing effects.
- Implements process priority introspection and mutation with `pc_highest`, `get_priority`, and `set_priority`.
- Implements `printm` and `interprint`, building formatted output in global `Buf` and routing through `dotag`.

Important interactions:
- `eval_sub` updates `LastStep`, consults `Rvous`, and delegates actual expression/statement effects to `eval`.
- `Enabled0` is used both by interactive simulation and scheduler selection to decide whether a process or option can proceed.
- Rendezvous sends call into queue logic and scheduler completion via the queue layer; `eval_sync` restricts the complementary side to synchronous receives.
- `pc_enabled` temporarily switches global `X` to another process, so callers must treat `X` as global mutable interpreter state.

Notable details:
- `TstOnly` suppresses side effects for trial execution.
- `E_Check` and `Escape_Check` prevent recursive enabled/escape probes from producing interactive prompts or visible side effects.
- Assertions call `wrapup(1)` unless running from an accepted trail mode.
- There is a duplicated `if (like_java)` line in the escape handling path; it is behaviorally redundant but worth preserving if doing mechanical source comparisons.
