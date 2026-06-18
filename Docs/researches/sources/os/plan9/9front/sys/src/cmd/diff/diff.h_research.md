# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diff.h

Shared declarations and data structures for Plan 9 `diff`.

Key elements:
- Defines `Line`, `Cand`, `Change`, and `Diff`.
- `Diff` holds original and pruned line arrays, equivalence classes, candidate lists, match vector `J`, file offsets, input buffers, binary flags, and collected changes.
- Declares global CLI state: `mode`, `bflag`, `rflag`, `mflag`, `anychange`, and `stdout`.
- Defines `MAXPATHLEN`, `MAXLINELEN`, `DIRECTORY`, and `REGULAR_FILE`.
- Declares memory helpers, pathname/temp/stat helpers, directory diff, regular diff, diff calculation, IO preparation, checking, change output, cleanup, and line reading.

Dependencies:
- Used by all files in `sys/src/cmd/diff`.

Research notes:
- Comments document deliberate memory overlaying inside `Diff` fields to reuse arrays during the diff algorithm.
