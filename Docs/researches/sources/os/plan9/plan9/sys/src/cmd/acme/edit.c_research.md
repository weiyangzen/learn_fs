# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/edit.c

This file parses Acme’s structural `Edit` command language and manages parse-time objects.

Key behavior:
- `cmdtab` defines command syntax, default addresses, regexp/text/address operands, counts, terminators, and executor function.
- `editcmd()` prepares command text, starts `editthread()`, waits for parse/exec completion, and applies edit logs to all affected windows.
- Lexer helpers read runes from command text, parse numbers, skip blanks, collect regexps/text/tokens, and validate delimiters.
- `parsecmd()` builds `Cmd` trees including nested `{}` blocks, command defaults, regexps, substitution RHS, and movement addresses.
- `simpleaddr()` and `compoundaddr()` build address parse trees.
- List/string/cmd allocation is tracked in global lists and freed by `freecmd()`.

Important details:
- Commands are automatically newline-terminated.
- Last regular expression is remembered for empty regexp reuse.
- Errors call `editerror()`, which frees parse objects, truncates edit logs, sends error text on `editerrc`, and exits the edit thread.
- Input length is capped relative to `RBUFSIZE`.

Filesystem relevance:
- Indirect but central to batch file editing through Acme’s `Edit` command.
