# File Research: sources/os/plan9/9front/sys/src/cmd/acid/util.c

This file provides Acid utility routines for symbols, registers, built-in variables, register reads, and garbage-collected string allocation.

Key responsibilities:
- `unique()` resolves symbol-name collisions by prepending `$`, printing rename diagnostics when not quiet.
- `varsym()` imports text/data/bss/local symbol-table entries into Acid variables and builds the `symbols` list as `{name, type, value}` triples.
- `varreg()` creates Acid variables for machine registers and a `registers` list; also exposes breakpoint instruction bytes as `bpinst`.
- `loadvars()` initializes standard Acid variables: `proc`, `pid`, `notes`, and `proclist`.
- `rget(map, reg)` reads a register value from a map using register metadata and format width.
- `strnodlen()`, `strnode()`, `runenode()`, `stradd()`, and `straddrune()` allocate Acid `String` objects and link them into the global GC list.
- `scmp()` compares two Acid strings by length and bytes.

Important dependencies:
- Uses libmach symbol and machine descriptions (`symbase`, `getsym`, `mach->reglist`, `machdata`).
- Uses global Acid allocation and symbol helpers (`gmalloc`, `mkvar`, `look`, `enter`, `gcl`).

Filesystem/storage relevance:
- No direct filesystem operations, but it bridges executable symbol tables and register maps into Acid's scripting environment.

Notes:
- Address format switches to 64-bit display (`Y`) when `mach->szaddr == 8`.
- Symbol import skips names beginning with `.` and long names that would overflow its stack buffer.
