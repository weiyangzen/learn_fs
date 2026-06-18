# File Research: sources/os/plan9/9front/sys/src/cmd/freq.c

## Purpose
Counts byte or Rune frequencies in input files.

## Key Elements
Parses output-format flags for decimal, hex, octal, character, and Rune mode; defaults to decimal/hex/octal/character for byte mode; counts stdin or each file into a `Runemax+1` array; prints only nonzero counts.

## Dependencies
Uses Plan 9 Bio `Bgetc`/`Bgetrune` and Rune constants.

## Behavior/Risks
The count array is large enough for all Runes, so memory is fixed and substantial. In byte mode, non-byte Rune values are only possible through array capacity, not input. Read errors are reported after counting.
