# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/sub1.c

Read fully: 621 lines, 10306 bytes. SHA-256 prefix: `778a1977c48bb5a9`.

This file contains front-half helpers for `lex`: diagnostics, input buffering, escapes, definition lookup, action copying, parse-tree construction, character-class intersection, duplication, and debug dumps.

Important routines:
- `printerr()`, `error()`, and `warning()` format source-aware messages.
- `lgate()` emits the generated header once.
- `cclinter()` refines packed character classes when a new class is seen.
- `usescape()` decodes C-style escapes and octal escapes.
- `lookup()` finds definitions/start conditions.
- `cpyact()` copies user action code, tracking braces, strings, comments, and `|` fallthrough pseudo-actions.
- `mn0()`, `mn1()`, `mn2()`, `mnp()` allocate parse-tree nodes and compute nullable state.
- `munputc()`/`munputs()` implement pushback.
- `dupl()` clones regex subtrees.
- debug-only routines print chars, strings, sections, and trees.

Integration: used directly by `parser.y` and later phases for parse-tree manipulation.

Risk notes: manual lexical copying of C actions is heuristic and must correctly handle comments/strings/braces to avoid corrupting generated scanner code.
