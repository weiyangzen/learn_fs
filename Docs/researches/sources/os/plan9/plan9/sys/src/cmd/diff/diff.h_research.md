# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diff.h

Shared header for Plan 9 `diff`. It declares global option flags: output `mode`, whitespace handling `bflag`, recursive directory flag `rflag`, multi-file context `mflag`, `anychange`, and external `stdout`/`binary`.

It defines allocation macros and `MAXPATHLEN`, then declares the cross-module functions for path construction, allocation, top-level dispatch, directory diffing, regular-file diffing, file preparation, error handling, line verification, change output, and context flush.

Integration points: consumed by `main.c`, `diffdir.c`, `diffio.c`, and `diffreg.c`.

Risks and notes: global mutable flags couple all modules. The header exposes only old-style C declarations and relies on external definitions rather than an encapsulated state object.
