# File Research: sources/os/plan9/9front/sys/src/cmd/sam/string.c

`string.c` implements sam's `String` rune-vector utilities.

It provides initialization with and without an initial NUL, close/free, reset with shrink for oversized buffers, rune-string length, duplication from NUL-terminated rune arrays or another `String`, append, ensure capacity with `STRSIZE` guard, insertion, deletion, comparison, prefix check, and conversion to UTF-8 C strings.

`Strcmp` intentionally treats an extra trailing NUL as equivalent in common cases because sam strings sometimes carry parser convenience NULs.

`tmprstr` wraps an existing rune slice in a static temporary `String` without copying. `tmpcstr` converts a UTF-8 C string into a newly allocated rune `String`, and `freetmpstr` releases it.
