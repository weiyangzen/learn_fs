# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/sched.c

This file owns Spin’s simulation scheduler, process/run lists, local variable runtime state, process creation, claim startup, rendezvous completion, and final reporting.

Global runtime state:
- `rdy` is the parsed process/proctype list.
- `run` is the active process list.
- `X` is the currently selected running process.
- `LastX`, `LastStep`, `nproc`, `nstop`, `Tval`, `Rvous`, `depth`, `nrRdy`, `Have_claim`, and `Skip_claim` control simulation state.
- `Priority_Sum` supports weighted random process selection.

Process lifecycle:
- `ready()` registers a parsed proctype/claim/init/trace in `rdy`.
- `runnable()` instantiates a `ProcList` into a `RunList`, assigns pid/priority, initializes program counter, and marks end states.
- `enable()` implements Promela `run`, checking `MAXP`, creating a runtime process, setting parameters, and initializing locals.
- `start_claim()` starts a selected never claim, moves it to pid 0, and shifts other pids.
- `wrapup()` prints final process/global/local state and process counts.

Scheduling:
- `pickproc()` chooses the next process by priority-weighted randomness or interactive user selection.
- `sched()` is the top-level driver. It handles table dump mode, product generation, verifier source generation, guided trail replay, then runs the random/interactive simulation loop.
- It evaluates provided clauses, calls `eval_sub()`, prints trace output, preserves atomic and d_step execution where required, detects blocked systems, enables timeout, and removes terminated processes.
- `silent_moves()` skips gotos, unless wrappers, atomic wrappers, and `.` pseudo-steps.

Rendezvous:
- `complete_rendez()` temporarily sets `Rvous`, searches another process for a matching synchronous receive, executes it, updates that process PC, and restores interactive state.

Local state:
- `addsymbol()`, `setlocals()`, `setparams()`, and `oneparam()` create per-process symbol tables.
- `findloc()`, `getlocal()`, and `setlocal()` resolve and mutate locals, including struct fields through `Rval_struct`/`Lval_struct`.

Remote references:
- `f_pid()`, `remotelab()`, and `remotevar()` resolve remote labels, `_p`, and remote variables, accounting for never-claim pid shifting.

Risk notes:
- Interactive mode stores choices in 256-sized arrays and skips pids above 255.
- Scheduler behavior depends heavily on global state and temporary context switches.
