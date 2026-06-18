# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.c

Source mapping and transition-text rendering support for generated verifier tables.

Key behavior:
- Maintains ordered source-state lists with `putsrc`, `putskip`, and `unskip`.
- `dumpsrc` emits `src_lnN[]` line-number arrays and `src_fileN[]` file-range maps for each process, then emits reached/loop-state data through `dumpskip`.
- Tracks skipped states separately so generated `reachedN[]` starts with states that do not need normal reachability reporting.
- Emits claim/event-trace aliases such as `src_claim`, `src_event`, and `reached_event`.
- `comment` renders a Promela AST node into readable source text for transition labels by using the recursive `comwork` printer.
- `comwork` handles constants/mtypes, expressions, `run`, channel operations, priority operations, receive variants, polling, guards, assignments, print/assert, remote references, embedded C placeholders, control constructs, atomic/d_step markers, and labels/gotos.
- Has special LTL-mode rendering for remote references and remote label equality.

Dependencies:
- Uses `putstmnt`, `putname`, `putremote`, `check_track`, `pid_is_claim`, and `sr_mesg` from other Spin generator/runtime files.
- Writes to generator output streams `tc` and `th`.

Research notes:
- This file is diagnostic/source-correlation infrastructure, but its output is also used by generated reachability checks and table diagnostics.
- Ordered insertion of source and skip records avoids duplicate state entries and keeps generated arrays deterministic.
