# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.c

This file generates source-line maps and readable statement comments for the verifier.

Key behavior:
- Tracks mapping from generated automaton states to Promela source lines and filenames.
- `putsrc()` records source line/file data for a state.
- `putskip()` and `unskip()` track states that should be marked reached even when they are synthetic or do not require normal reachability checks.
- `dumpsrc()` emits `src_lnN[]`, `src_fileN[]`, `src_claim`, and event-source aliases into `pan.h`.
- `dumpskip()` emits `reachedN[]` and `loopstateN` declarations.
- `comment()` renders AST nodes as compact Promela-like source text for transition labels.
- `comwork()` handles expression, channel, send/receive, run, print, assert, remote reference, `atomic`, `d_step`, `unless`, `timeout`, and control-flow syntax.

Important details:
- File ranges are compressed into `S_F_MAP` entries with filename plus state interval.
- `comment()` forces terse/no-cast printing so generated transition labels are source-like rather than executable C.
- In LTL mode, remote references are rendered in user-facing forms like `proc@label`.
- Mtype constants can be printed symbolically via `symbolic()`/`sr_mesg()`.
- Source maps support claim-specific `src_claim` and event-specific `src_event` aliases.

Filesystem relevance:
- Indirect. It records source filenames and line ranges for generated verifier diagnostics, not filesystem behavior.
