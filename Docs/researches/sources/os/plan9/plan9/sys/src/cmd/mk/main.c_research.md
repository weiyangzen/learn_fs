# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/main.c

Main entry point for Plan 9 `mk`.

Responsibilities:
- Parses command-line flags and assignment arguments.
- Initializes symbol table, environment, mk variables, and parsed mkfiles.
- Determines default or explicit targets and invokes `mk()`.
- Supports profiling, debug dumping, what-if times, and usage accounting.

Important flags:
- `-a` force all, implies `-i`.
- `-d[peg]` debug parser/graph/exec.
- `-e` explain.
- `-f file` mkfile.
- `-i`, `-k`, `-n`, `-s`, `-t`, `-u`, `-w`.

Key variables:
- Global flags, `rules`, `metarules`, `target1`, `jobs`, `patrule`, and output `bout`.

Behavior notes:
- Assignment args are written into a temporary file and parsed as override assignments.
- `MKFLAGS` and `MKARGS` are synthesized.
- With multiple explicit targets and no `-s`, it creates a virtual aggregate rule.
