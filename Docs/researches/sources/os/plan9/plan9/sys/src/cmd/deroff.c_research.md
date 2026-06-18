# File Research: sources/os/plan9/plan9/sys/src/cmd/deroff.c

This file implements `deroff`, a troff/eqn/tbl/pic stripper that can output plain text or one word per line.

Key behaviors:
- Supports options:
  - `-w`: output one word per line.
  - `-_`: word mode preserving underscores inside words.
  - `-m m`, `-m s`, `-m l`: interpret MM/MS/list macro behavior.
  - `-i`: ignore `.so` and `.nx` includes.
- Reads through helper macros `C`/`C1`, implemented as `fC()`/`fC1()`, tracking line count and inline eqn delimiters.
- `work()` dispatches command lines to `comline()` and ordinary lines to `regline()`.
- `regline()` strips troff backslash constructions and either prints the line, macro-filtered text, or words.
- `putwords()` classifies runes and emits word tokens by the historical deroff definition.
- `comline()` handles troff commands, macro definitions, includes, next-file directives, eqn/table/pic blocks, MS/MM display macros, references, and selected macros like `.UX`.
- `eqn()` skips `.EQ`/`.EN` regions and tracks `delim` declarations for inline equations.
- `tbl()`/`stbl()` skip table regions.
- `sdis()` skips display/list-like macro regions.
- `backsl()` parses and removes troff escape constructions.
- `inpic()` extracts quoted text from pic input when applicable.
- `getfname()` opens `.so`/`.nx` targets while avoiding directories, non-mounted files, tmac files, and repeated includes.

Notable implementation details:
- Maintains a stack of up to 15 input files.
- `charclass()` treats non-ASCII runes as `EXTENDED`, except en/em dash are special separators.
- The source has duplicate `infile` declarations in the Plan 9 style block, but the effective code uses the later `Biobuf *infile`.
- The macro-skipping logic is highly stateful through globals such as `msflag`, `mac`, `disp`, `inmacro`, `intable`, `eqnflag`, `ldelim`, and `rdelim`.
