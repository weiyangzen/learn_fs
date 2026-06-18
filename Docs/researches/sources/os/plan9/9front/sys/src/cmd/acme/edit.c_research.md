# File Research: sources/os/plan9/9front/sys/src/cmd/acme/edit.c

This file parses Acme's edit command language and orchestrates edit-thread execution.

Key responsibilities:
- Defines `cmdtab`, mapping command characters to parse requirements, default addresses, default commands, token rules, and executor functions.
- `editcmd()` prepares command text, initializes edit logs on all windows, starts `editthread()`, waits for errors, then applies pending edit logs.
- `editthread()` repeatedly parses and executes commands.
- `editerror()` frees parse state, terminates all edit logs, reports the error through `editerrc`, and exits the edit thread.
- Lexer/parser utilities: `getch()`, `nextc()`, `ungetch()`, `getnum()`, `cmdskipbl()`, `okdelim()`, `atnl()`.
- Dynamic list helpers manage parse allocations for commands, addresses, and strings.
- String helpers allocate and grow command strings.
- `collecttext()`, `collecttoken()`, `getrhs()`, `getregexp()` parse command arguments.
- `parsecmd()` parses addresses, commands, grouped blocks, regexes, counts, text, tokens, and default commands.
- `simpleaddr()` and `compoundaddr()` parse address ASTs.

Important dependencies:
- Execution is delegated to `ecmd.c`.
- Uses `elogterm()`/`elogapply()` to manage deferred changes.
- Uses `allwindows()` to initialize/apply edits across all open windows.

Filesystem/storage relevance:
- Indirect but central to file editing: this parser drives edits that may read, write, and pipe file content through `ecmd.c`.

Notes:
- Command input is rune-based and NUL-terminated.
- There is a command length guard based on `RBUFSIZE`.
- Last regex is remembered for empty regex reuse.
