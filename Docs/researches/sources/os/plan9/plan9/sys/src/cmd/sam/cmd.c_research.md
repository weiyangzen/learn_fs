# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/cmd.c

Read status: complete, 607 lines.

This file parses `sam` commands. `cmdtab` defines command characters, whether they take text/regexp/address/count/token operands, default commands, default addresses, and executor functions.

Input can come from stdin or the downloaded terminal protocol. `inputc`, `inputline`, `getch`, `ungetch`, `skipbl`, and `getnum` implement rune-aware command input. `cmdloop` repeatedly parses and executes commands, updating the terminal state when downloaded.

`parsecmd` parses addresses, command names, nested `{}` blocks, regexps, substitution RHS text, command text blocks, and tokens. `getregexp`, `simpleaddr`, and `compoundaddr` implement regexp reuse and address grammar.

Temporary parse objects are tracked in `List` instances and freed by `freecmd`.

Filesystem relevance: controls editor commands that eventually read, write, and modify files, but this file is parser logic rather than direct I/O.
