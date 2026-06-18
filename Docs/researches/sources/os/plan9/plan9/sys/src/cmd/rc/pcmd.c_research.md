# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/pcmd.c

Pretty-printer from rc parse trees back to rc source.

Main functions:
- `pdeglob()` prints a word without internal `GLOB` escape bytes.
- `pcmd()` recursively formats every tree type: variables, quoted vars, async, concatenation, backquote, logical operators, blocks, loops, conditionals, switch, match, assignments, redirections, fd duplication, pipes, words, and arg lists.

Uses:
- Function body serialization in `code.c`.
- Debugging and `whatis` output through `io.c` formatting.

Risk/notes:
- Global `nl` switches command separator output between newline and semicolon for function serialization.
- Some fd duplication print order follows lexer-internal representation.
