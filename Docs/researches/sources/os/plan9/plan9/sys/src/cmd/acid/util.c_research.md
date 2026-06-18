# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/util.c

This file initializes Acid variables from symbols/register metadata and provides string/value helpers.

Key behavior:
- `varsym()` imports linker/debug symbols into Acid variables, renaming collisions by prefixing `$`, and builds a `symbols` list of `{name,type,value}` triples.
- `varreg()` exports machine register names as Acid variables and populates a `registers` list; also creates `bpinst` from architecture breakpoint instruction bytes.
- `loadvars()` initializes default variables: `proc`, `pid`, `notes`, and `proclist`.
- `rget()` reads 32-bit or 64-bit register values from a `Map` depending on register format.
- String constructors allocate GC-linked `String` objects for byte strings, rune strings, concatenation, rune append, and equality.

Important details:
- Symbol name conflicts are resolved conservatively but stop warning after repeated renames.
- String lengths are byte lengths in this Acid representation, including rune-copy paths that store raw rune bytes.
- `rget()` relies on register offsets placed in variables by `varreg()`.

Filesystem relevance:
- Indirect: prepares debugger state used when reading process/core maps.
