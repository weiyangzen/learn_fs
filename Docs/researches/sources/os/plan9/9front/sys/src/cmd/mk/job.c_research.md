# File Research: sources/os/plan9/9front/sys/src/cmd/mk/job.c

Allocates, frees, and dumps `Job` objects representing runnable recipes.

Key behavior:
- `newjob()` stores rule, node list, stem/matches, prerequisite lists, target lists, and initializes scheduling fields.
- `freejob()` frees word-list fields after a job completes.
- `dumpj()` prints job internals for execution debugging.

Important dependencies: `mk.h`, `Word` ownership helpers, `wtos`.

Notable risks:
- `stem` and `match` are borrowed from arcs, not freed by `freejob()`.
