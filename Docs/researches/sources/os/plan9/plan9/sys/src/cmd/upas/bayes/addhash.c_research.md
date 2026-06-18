# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/addhash.c

- Role: Merges one or more serialized token hash tables with integer scaling factors.
- Control flow: Reads pairs of `file scale`, accumulates counts into global `Hash`, optionally creates an exclusive output file with retry-on-lock, writes merged hash.
- Integration: Uses `Breadhash`, `Bwritehash`, and `Bopenlock` from `hash.c`.
- Risks/notes: Rejects scale zero; old entries may be dropped by `Bwritehash` date aging.
