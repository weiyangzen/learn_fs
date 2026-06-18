# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.c

This is Spin’s central `pan` verifier code generator. It writes the generated verifier source files (`pan.c`, `pan.h`, `pan.t`, `pan.m`, `pan.b`, or separate-claim variants), emits transition tables, and translates Promela AST statements into executable C forward and reverse moves.

Key behavior:
- `gensrc()` opens all generated `pan*` output files, emits compile-time feature macros, includes generated template fragments, writes process transition tables, and emits runtime helpers.
- Supports normal, separate source, and separate claim generation through `separate` and `Cfile[]`.
- Generates metadata for claims, event traces, non-progress monitoring, `np_`, fairness, rendezvous, sorted/random receive, `xr`/`xs`, `provided`, `enabled`, `pc_value`, `timeout`, and embedded C code.
- `putproc()`, `put_seq()`, `put_el()`, and `put_sub()` walk process FSM sequences and emit `Trans` table entries plus forward/reverse case labels.
- `case_cache()` emits reusable forward/backward cases, handles merge chains, records backup values for undo, and avoids duplicate emitted code where possible.
- `putstmnt()` translates each Promela AST node into generated C: expressions, assignments, sends, receives, polls, run, asserts, printf, channel operations, remote references, embedded C, and process deletion.
- `putname()` resolves variable references into generated state-vector access paths, including local process structs, globals, arrays, structures, `_pid`, `_`, and hidden names.
- `genconditionals()` emits partial-order reduction conditional-safety tables based on channel reference classes.
- `has_global()` classifies statements and expressions as local/global for partial-order reduction and merge safety.
- `count_runs()` and `any_runs()` enforce restrictions on `run` placement.

Important details:
- This file is tightly coupled to global Spin compiler state from `spin.h`, parser node tags from `y.tab.h`, and template arrays from `pangen2.h`, `pangen4.h`, and `pangen5.h`.
- Forward moves are emitted to `pan.m`; backward undo moves are emitted to `pan.b`; transition metadata is emitted to `pan.t`; shared declarations go to `pan.h`.
- `multi_oval`, `CnT`, and `YZ` track multiple backup values needed to undo merged transitions or receive assignments.
- Receive generation handles normal receive, random receive, poll receive, constant/eval match fields, `_` discard fields, rendezvous blocking, GUI trail display, and fairness counter undo.
- Send generation handles lossy send, sorted send, rendezvous handshakes, `xr`/`xs` checking, and GUI trail display.
- Merge optimization can chain nonblocking safe statements while preserving labels and reverse execution.
- Partial-order reduction safety depends on channel name IDs, not concrete runtime queue IDs, because channel arrays can map to many queues.
- Event-trace processes are special-cased so their send/receive code validates observed operations rather than mutating normal process state.

Filesystem relevance:
- Indirect. This file is not filesystem implementation code, but it creates generated verifier files on disk and emits code that may write trails/checkpoints via other templates.
