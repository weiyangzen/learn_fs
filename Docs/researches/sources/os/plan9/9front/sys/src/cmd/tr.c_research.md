# File Research: sources/os/plan9/9front/sys/src/cmd/tr.c

Read completely: 354 lines, 5975 bytes.

Plan 9 UTF-aware `tr` implementation. It supports delete, complement, squeeze, range syntax, octal escapes, and `\x` hexadecimal escapes over `Rune` values up to `Runemax`.

Key behavior:
- `delete` builds a bitset for characters to delete, with optional squeeze set.
- `translit` maps runes from string1 to string2, repeats the last target rune when string2 is shorter, and detects ambiguous source mappings.
- `complement` builds a mapping for all runes not in string1 up to the highest rune mentioned.
- `readrune` buffers stdin until a full UTF rune is available; `writerune` buffers output.
- `canon` expands `a-b` ranges while validating ordering.

Reliability notes:
- Bitsets are sized for all Plan 9 runes, so memory is fixed but large.
- Complement allocation is proportional to highest specified rune, which can be large.
