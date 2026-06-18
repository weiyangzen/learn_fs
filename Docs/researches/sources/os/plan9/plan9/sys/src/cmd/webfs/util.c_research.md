# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/util.c

This file provides allocation and string helpers for `webfs`.

Functions:
- `erealloc`: fatal realloc with allocation tag.
- `emalloc`: zeroing fatal malloc with allocation tag.
- `estrdup`: fatal strdup with allocation tag.
- `estredup`: duplicates a `[s,e)` substring and NUL-terminates.
- `estrmanydup`: concatenates a varargs list of strings into a new allocation.
- `strlower`: lowercases ASCII letters in place.

Notable issue:
- `estrmanydup` calls `va_start` twice but only calls `va_end` once; this is non-idiomatic varargs handling.
