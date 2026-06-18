# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/tree.c

AST allocation and manipulation helpers for rc.

Main functions:
- `newtree()` allocates zeroed tree nodes and links them into the parse allocation list.
- `freenodes()` frees all parse-time nodes after command compilation.
- `tree1()`, `tree2()`, `tree3()` construct nodes and simplify null `;` nodes.
- `mung1()`, `mung2()`, `mung3()` mutate lexer-created nodes with children.
- `epimung()` attaches redirection epilogues around compound commands.
- `simplemung()` wraps simple commands, records printable command text, and hoists redirections from arg lists to the command root.
- `token()` creates word/keyword nodes.
- `freetree()` recursively frees a standalone tree.

Risk/notes:
- `simplemung()` depends on tree shape produced by grammar and lexer.
- Parse nodes are normally arena-like via `treenodes`; `freetree()` is separate for explicit ownership cases.
