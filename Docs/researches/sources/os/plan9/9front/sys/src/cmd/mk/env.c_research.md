# File Research: sources/os/plan9/9front/sys/src/cmd/mk/env.c

Manages mk’s variable environment for recipe execution.

Key behavior:
- Registers internal variables such as `target`, `stem`, `prereq`, `pid`, `nproc`, `newprereq`, `alltarget`, `newmember`, and `stem0` through `stem9`.
- `initenv()` marks internal variables and imports the OS environment.
- `execinit()` resets internal variables and builds an export list from non-internal, exportable mk variables.
- `buildenv()` fills internal variables for a job, extracts archive member names into `newmember`, and populates regexp stem captures.

Important dependencies: `mk.h`, symbol-table spaces `S_INTERNAL`, `S_VAR`, `S_NOEXPORT`.

Notable risks:
- Internal variables are mutable global symbols reused per job.
- `newmember` mutates duplicated prerequisite word strings while extracting text between parentheses.
