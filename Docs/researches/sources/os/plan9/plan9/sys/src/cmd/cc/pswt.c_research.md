# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pswt.c

This file handles switch-case table preparation plus a few codegen helpers.

Key behavior:
- Sorts and validates switch cases in `doswit()`, detects duplicate cases, supplies default targets, and delegates compact switch emission to `swit1()`.
- Handles 64-bit switch expressions on 32-bit machines by switching on high words then low words.
- Allocates case records with `casf()`.
- Emits wide string storage with `outlstring()`.
- Provides unused-result warning support through `nullwarn()`.
- Converts native doubles into compiler `Ieee` representation with `ieeedtod()`.

Important details:
- 32-bit switch expressions with 64-bit case constants are warned about and impossible cases are skipped.
- Wide string output honors target byte order via alignment behavior.
- Switch emission depends on architecture-provided `swit1()`.

Filesystem relevance:
- Indirect compiler code generation.
