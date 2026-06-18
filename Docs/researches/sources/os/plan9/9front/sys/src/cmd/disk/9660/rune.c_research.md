# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/rune.c

Small rune-string helper library for Joliet support.

Key behavior:
- `strtorune` converts UTF-8 `char *` to a null-terminated `Rune *`.
- `runechr` finds a rune in a rune string.
- `runecmp` lexicographically compares rune strings.

Research notes:
- Callers provide output buffers; there is no bounds checking in this helper.
