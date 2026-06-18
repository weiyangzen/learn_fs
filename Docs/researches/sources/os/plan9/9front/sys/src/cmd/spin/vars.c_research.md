# File Research: sources/os/plan9/9front/sys/src/cmd/spin/vars.c

`vars.c` implements runtime access, initialization, assignment, casting, and reporting for PROMELA variables during simulation.

Key responsibilities:
- Provides `getval` and `setval`, dispatching to local or global storage depending on `Symbol.context`.
- Rejects assignments to reserved predefined variables such as `_p`, `_pid`, `_nr_qs`, and `_nr_pr`, with compatibility behavior for old priority rules.
- Removes self-referential initializers with `rm_selfrefs`.
- Initializes variable storage lazily in `checkvar`, allocating arrays and evaluating initializers.
- Reads and writes global variables with `getglobal` and `setglobal`, delegating struct fields to `Rval_struct`/`Lval_struct`.
- Casts values according to PROMELA type widths in `cast_val`, including bit, byte, short, and unsigned-width masking.
- Dumps claim state with `dumpclaims`.
- Dumps visible/tracked globals with `dumpglobals`, including queues, structs, MSC output, and column-output mode.
- Dumps local variables for a process with `dumplocal`, including queues, structs, tracked locals, and MSC output.

Important interactions:
- `run.c` uses `getval`, `setval`, and `cast_val` through expression evaluation.
- `sched.c` calls `checkvar`, `getlocal`, and `setlocal`.
- Structure access is delegated to `structs.c`; queues are delegated to message/queue helpers.
- Visibility and tracking are controlled by symbol `hidden` flags and global verbosity flags.

Notable details:
- `setat` depth is used to suppress or include recently changed variables in trace-style output.
- `limited_vis` and `no_arrays` affect dump filtering.
