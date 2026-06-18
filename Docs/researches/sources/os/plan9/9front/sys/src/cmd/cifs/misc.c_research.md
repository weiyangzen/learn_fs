# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/misc.c

Contains two in-place ASCII case conversion helpers: `strupr` and `strlwr`.

Each walks a mutable C string and applies `toupper`/`tolower` only after checking the byte is non-negative and currently lower/upper case.

Used by CIFS command setup and name normalization, notably share names from command-line arguments in `main.c`.

Scope is intentionally tiny; no allocation, locale, or Unicode handling.
