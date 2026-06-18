# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/address.c

Read status: complete, 240 lines.

This file evaluates `sam` addresses. It supports character and line addresses, dot, end-of-file, mark, forward/backward regexp search, file-name matching, whole-file selection, comma/semicolon ranges, and relative `+`/`-` movement.

`nextmatch` compiles and executes regexps with wrap behavior for zero-length matches. `matchfile` and `filematch` match file menu entries against a regexp. `charaddr` and `lineaddr` implement bounds-checked character and line range movement.

Filesystem relevance: editor addressing over in-memory file buffers; indirect filesystem relation through file selection by name/menu.
