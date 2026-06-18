# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/hideset.c

Macro hideset table used to prevent recursive macro re-expansion. A hideset is a sorted, null-terminated array of `Nlist*`, referenced by index from tokens.

Important behavior:
- Hideset 0 is the empty set.
- `newhideset()` inserts a macro into an existing set, interns identical sets, and grows the global set table.
- `unionhideset()` repeatedly adds all symbols from one hideset into another.
- `checkhideset()` tests membership and aborts on invalid indices.
- Maximum per-set size is constrained by `HSSIZ`.
