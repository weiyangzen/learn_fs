# File Research: sources/os/plan9/9front/sys/src/cmd/db/pcs.c

Purpose: User command layer for process control in `db`.

Key behavior:
- `subpcs()` implements `:` commands:
  - `:b`/`:B` set normal/temporary breakpoints with optional commands.
  - `:d`/`:D` delete breakpoints.
  - `:r`/`:R` restart/run.
  - `:s` single-steps instructions.
  - `:S` steps source lines.
  - `:c`/`:C` continues.
  - `:n` manages pending notes.
  - `:h` stops/grabs a process.
  - `:x` resumes/ungrabs.
  - `:k` kills.
- After runs, it removes installed breakpoints, prints current pc, and prints pending notes.

Notable details:
- Breakpoint commands with no explicit count become effectively infinite by setting `HUGEINT`.
- Source-line stepping uses `pc2line()` and loops until the line changes.
