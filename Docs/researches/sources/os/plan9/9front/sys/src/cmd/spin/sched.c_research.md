# File Research: sources/os/plan9/9front/sys/src/cmd/spin/sched.c

`sched.c` owns Spin's simulation process tables, scheduling loop, process creation, never-claim startup, rendezvous completion, and runtime local-variable storage. It is central to the interpreter mode and code-generation handoff.

Key responsibilities:
- Defines global runtime state: `run`, `X`, `LastX`, `rdy`, `LastStep`, `nproc`, `nstop`, `depth`, `Tval`, `Rvous`, `Priority_Sum`, `Have_claim`, and `Skip_claim`.
- Registers proctypes/claims/traces with `ready`, and instantiates runtime processes with `runnable`.
- Starts processes from `run` expressions with `enable`, validates parameter counts, binds actuals to formals, and initializes local variables.
- Starts a selected never claim with `start_claim`, reorders it to pid 0, and adjusts process pids.
- Implements final reporting in `wrapup`, including globals, locals, process states, and MSC/postlude output.
- Implements scheduling in `sched`, including code-generation mode, product generation, trail replay, random simulation, interactive selection, timeout handling, process termination, atomic-chain preservation, and blocked-process detection.
- Completes synchronous rendezvous operations with `complete_rendez`.
- Implements local runtime symbol lookup and mutation through `findloc`, `getlocal`, `setlocal`, `in_bound`, `addsymbol`, `setlocals`, and `setparams`.
- Implements remote label and variable references with `remotelab` and `remotevar`.

Important interactions:
- `sched` repeatedly chooses a process with `pickproc`, executes through `eval_sub`, and writes the resulting element back to the process `pc`.
- `pickproc` uses priorities, `provided` guards, `Enabled0`, and optional interactive menus to choose a runnable process.
- `complete_rendez` temporarily sets `Rvous`, suppresses interactivity, and scans other processes for a matching synchronous receive.
- `remotevar` temporarily switches `X` to evaluate another process' local variable.

Notable details:
- `silent_moves` collapses labels/gotos/compound wrappers before interactive presentation and after atomic/rendezvous steps.
- Priority behavior has compatibility branching for `old_priority_rules`.
- `enabled()` is rejected for models with synchronous channels.
- The file has a few duplicated statements/returns in the local tree (`Have_claim = 1`, `if (X->pc && X->pc->n)`, a duplicated `return cast_val` line); they appear redundant rather than intentional new behavior.
