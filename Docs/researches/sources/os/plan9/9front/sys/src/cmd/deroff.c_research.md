# File Research: sources/os/plan9/9front/sys/src/cmd/deroff.c

Purpose: Strips troff/nroff, eqn, tbl, pic, and macro constructs from text, optionally emitting one word per line.

Key behavior:
- Supports `-w`, `-_`, `-m m|s|l`, and `-i`.
- Maintains an input file stack for `.so` includes and `.nx` next-file directives unless `-i`.
- `work()` loops over regular lines and command lines.
- `regline()` reads ordinary text lines, strips backslash constructs, preserves selected table text, and emits raw line, macro-filtered line, or words.
- `putwords()` tokenizes output into words using custom character classes.
- `comline()` recognizes and skips/interprets troff commands: comments, `.EQ/.EN`, `.TS/.TE`, macro definitions, `.so`, `.nx`, `.tm`, `.hw`, section/title/list/display macros, pic, centered text, references, etc.
- `eqn()` skips display equations and tracks inline equation delimiters.
- `skeqn()` skips inline equations delimited by configured eqn delimiters.
- `tbl()`/`stbl()` skip table control.
- `sdis()`, `sce()`, `refer()`, and `inpic()` handle macro package display, centered text, references, and pic quoted text.
- `backsl()` skips troff escape constructs and handles selected escapes such as em dash under ms mode.

Notable details:
- Character classes distinguish special, apostrophe, punctuation, digit, letter, and extended runes.
- Include-loop prevention uses a linked list of seen file names.
- `msflag` changes behavior substantially for ms/mm macro packages.
