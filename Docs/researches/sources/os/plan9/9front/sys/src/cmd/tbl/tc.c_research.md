# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tc.c

Chooses internal delimiter characters for marking table field boundaries in generated troff.

Key points:
- `choochar` scans all real cell text and right-column text for ASCII characters already present.
- It chooses `F1` and `F2` from a priority string of uncommon control/punctuation/letter characters, falling back through `Y` and `u`.
- Fails if two unused delimiters cannot be found.
- `point` classifies a `char *` value as a real pointer versus a small encoded sentinel by checking whether the cast address is at least 128.

Dependencies and interactions:
- Used by output code that wraps fields with `F1` and `F2`.
- Depends on `ctype`, `point`, `table`, `instead`, `fullbot`, `nlin`, and `ncol`.

Research relevance:
- This file protects generated troff field delimiters from colliding with user table text.
